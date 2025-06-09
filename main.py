from flask import Flask, request, jsonify
import requests
import logging
import time
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

BITRIX_WEBHOOK = os.getenv("BITRIX_WEBHOOK")
FIELD_RESP_ORIGINAL = os.getenv("FIELD_RESP_ORIGINAL")

logging.basicConfig(level=logging.INFO)

def extrair_numero(string):
    return string.split("_")[-1]

@app.route("/change-the-chat-channel/", methods=["POST"])
def change_the_chat_channel():
    CONTACT_ID = request.args.get("CONTACT_ID")
    QUEUE_ID = request.args.get("QUEUE_ID")

    if not CONTACT_ID or not QUEUE_ID:
        return jsonify({"error": "CONTACT_ID and QUEUE_ID must be provided in the URL parameters"}), 400

    base_url = BITRIX_WEBHOOK
    url = f"{base_url}/imopenlines.crm.chat.getLastId?CRM.ENTITY_TYPE=CONTACT&CRM_ENTITY={CONTACT_ID}"

    logging.info(f"Buscando ID do chat: {url}")
    response = requests.post(url)
    time.sleep(2)

    if response.status_code == 200:
        id_chat = response.json()["result"]
        url2 = f"{base_url}/imopenlines.operator.transfer?CHAT_ID={id_chat}&QUEUE_ID={QUEUE_ID}"
        logging.info(f"Transferindo chat para fila: {url2}")
        response2 = requests.post(url2)

        if response2.status_code == 200:
            return "New responsible approved"
        else:
            return f"No responsible approved: {response2.text}"
    else:
        return f"Failed to get chat ID: {response.text} - {url}"


@app.route("/change-the-chat-responsible/", methods=["POST"])
def change_the_chat_responsability():
    CONTACT_ID = request.args.get("CONTACT_ID")
    TRANSFER_ID = request.args.get("TRANSFER_ID")

    if not CONTACT_ID or not TRANSFER_ID:
        return jsonify({"error": "CONTACT_ID and TRANSFER_ID must be provided in the URL parameters"}), 400

    TRANSFER_ID = extrair_numero(TRANSFER_ID)

    base_url = BITRIX_WEBHOOK
    url = f"{base_url}/imopenlines.crm.chat.getLastId?CRM.ENTITY_TYPE=CONTACT&CRM_ENTITY={CONTACT_ID}"

    logging.info(f"Buscando chat para contato {CONTACT_ID}")
    response = requests.post(url)
    time.sleep(2)

    if response.status_code == 200:
        id_chat = response.json()["result"]
        url2 = f"{base_url}/imopenlines.operator.transfer?CHAT_ID={id_chat}&TRANSFER_ID={TRANSFER_ID}"
        logging.info(f"Transferindo chat para responsável {TRANSFER_ID}")
        response2 = requests.post(url2)

        if response2.status_code == 200:
            return "New responsible approved"
        else:
            logging.warning(f"Erro na transferência de responsável: {response2.text}")
            return f"No responsible approved: {response2.text}"
    else:
        logging.error(f"Erro ao buscar ID do chat: {response.text}")
        return f"Failed to get chat ID: {response.text}"


@app.route("/finalize-chat/", methods=["POST"])
def finalize_chat():
    DEAL_ID = request.args.get("DEAL_ID")

    if not DEAL_ID:
        return jsonify({"error": "DEAL_ID must be provided in the URL parameters"}), 400

    base_url = BITRIX_WEBHOOK
    url_get_chat = f"{base_url}/imopenlines.crm.chat.get?CRM_ENTITY_TYPE=DEAL&CRM_ENTITY={DEAL_ID}"

    response = requests.get(url_get_chat)
    time.sleep(2)

    if response.status_code == 200:
        datajson = response.json()
        logging.info(f"Response JSON: {datajson}")

        if "result" in datajson and isinstance(datajson["result"], list) and len(datajson["result"]) > 0:
            chat_id = datajson["result"][0]["CHAT_ID"]
            url_finish_chat = f"{base_url}/imopenlines.operator.another.finish?CHAT_ID={chat_id}"
            response2 = requests.post(url_finish_chat)

            if response2.status_code == 200:
                return jsonify({"status": "success", "message": "Chat finalized successfully"})
            else:
                return jsonify({"error": "Failed to finalize chat", "details": response2.text}), 500
        else:
            return jsonify({"error": "CHAT_ID not found in response"}), 404
    else:
        return jsonify({"error": "Failed to get CHAT_ID", "details": response.text}), 500


@app.route("/transfer-chat-between-deals/", methods=["POST", "GET"])
def transfer_chat_between_deals():
    from_id = request.args.get("from_deal_id", "Não informado")
    to_id = request.args.get("to_deal_id", "Não informado")

    if from_id == "Não informado" or to_id == "Não informado":
        return {"status": "error", "message": "ID do deal não informado!"}, 400

    base_url = BITRIX_WEBHOOK
    url_get_activity = f"{base_url}/crm.activity.list?filter[OWNER_ID]={from_id}"
    res = requests.get(url_get_activity)

    if len(res.json()["result"]) < 1:
        return {"status": "error", "message": f"Não há atividades para serem movidas no card {from_id}"}, 404

    activity_id = res.json()["result"][0]["ID"]
    url_move = f"{base_url}/crm.activity.binding.move"

    payload = {
        "activityId": activity_id,
        "sourceEntityId": from_id,
        "targetEntityId": to_id,
        "sourceEntityTypeId": 2,
        "targetEntityTypeId": 2,
    }

    res2 = requests.get(url=url_move, params=payload)

    if res2.status_code == 200:
        return {
            "status": "success",
            "message": f"Atividade movida do Card número {from_id} para o Card número {to_id}",
        }, 200

    return {"status": "error", "message": res2.json().get("error_description", "Erro desconhecido")}, 500


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    deal_id = request.form.get('data[FIELDS][ID]')

    if not deal_id:
        return jsonify({'status': 'erro', 'mensagem': 'ID do negócio não encontrado'}), 400

    response = requests.get(f"{BITRIX_WEBHOOK}/crm.deal.get", params={'id': deal_id})
    result = response.json().get('result', {})

    if result["CLOSED"] == "Y" :
        return jsonify({"status": "error", "message": "Negócio esta fechado"}), 400

    assigned_by = str(result.get('ASSIGNED_BY_ID', ''))
    original_responsible = str(result.get(FIELD_RESP_ORIGINAL, ''))
    contact_id = str(result.get('CONTACT_ID', ''))

    if not original_responsible or original_responsible == 'None':
        update = requests.post(f"{BITRIX_WEBHOOK}/crm.deal.update", json={
            'id': deal_id,
            'fields': {
                FIELD_RESP_ORIGINAL: assigned_by
            }
        }).json()
        logging.info(f"Responsável original registrado: {assigned_by}")
        return jsonify({'status': 'atualizado', 'mensagem': 'Responsável original registrado'})

    elif original_responsible != assigned_by:
        update = requests.post(f"{BITRIX_WEBHOOK}/crm.deal.update", json={
            'id': deal_id,
            'fields': {
                FIELD_RESP_ORIGINAL: assigned_by
            }
        }).json()
        logging.info(f"Responsável mudou: de {original_responsible} para {assigned_by} — Campo atualizado")

        # Chamada interna à rota /change-the-chat-responsible/
        try:
            with app.test_request_context(
                f"/change-the-chat-responsible/?CONTACT_ID={contact_id}&TRANSFER_ID={assigned_by}",
                method="POST"
            ):
                transfer_response = change_the_chat_responsability()

                status_code = (
                    transfer_response[1]
                    if isinstance(transfer_response, tuple)
                    else 200
                )

                if status_code == 200:
                    logging.info(f"Transferência de responsabilidade feita com sucesso para {assigned_by}")
                else:
                    logging.warning(f"Falha na transferência de responsabilidade: {transfer_response}")
        except Exception as e:
            logging.error(f"Erro ao executar change_the_chat_responsability: {e}")

        return jsonify({'status': 'mudou', 'mensagem': 'Responsável mudou, campo atualizado e chat transferido'})

    else:
        logging.info("Não mudou a responsabilidade")
        return jsonify({'status': 'sem_mudança', 'mensagem': 'Não mudou a responsabilidade'})


if __name__ == "__main__":
    app.run(port=1470, host="0.0.0.0")
