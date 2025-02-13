def get_palometa_data():
    try:
        palometa_data = list(db.peces.find({"nombre": "Palometa"}))
        for data in palometa_data:
            data['_id'] = str(data['_id'])
        return jsonify(palometa_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500