import os
import csv
import logging
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = "pemsd7"
COL_NAME  = "stations"
CSV_PATH  = os.path.join(os.path.dirname(__file__), "data", "PeMSD7_stations.csv")

def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]

def load_csv_to_mongo():
    db  = get_db()
    col = db[COL_NAME]
    col.create_index("station_id", unique=True)

    inserted = skipped = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lanes = int(row["lanes"]) if row.get("lanes") and row["lanes"] != "0" else 1
            except:
                lanes = 1
            try:
                abs_pm = float(row["abs_postmile"]) if row.get("abs_postmile") else 0.0
            except:
                abs_pm = 0.0

            doc = {
                "station_id"   : int(row["station_id"]),
                "freeway"      : row["freeway"],
                "direction"    : row["direction"],
                "abs_postmile" : abs_pm,
                "latitude"     : float(row["latitude"]),
                "longitude"    : float(row["longitude"]),
                "lanes"        : lanes,
                "type"         : row.get("type", "ML"),
                "type_desc"    : row.get("type_desc", "Mainline"),
                "name"         : row.get("name", ""),
                "location": {
                    "type": "Point",
                    "coordinates": [float(row["longitude"]), float(row["latitude"])]
                }
            }
            try:
                col.insert_one(doc)
                inserted += 1
            except DuplicateKeyError:
                skipped += 1

    logger.info(f"CSV import: {inserted} inserted, {skipped} skipped.")
    return inserted, skipped

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/import", methods=["POST"])
def api_import():
    try:
        inserted, skipped = load_csv_to_mongo()
        return jsonify({"status": "ok", "inserted": inserted, "skipped": skipped})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/stations", methods=["GET"])
def api_stations():
    try:
        db  = get_db()
        col = db[COL_NAME]

        freeway   = request.args.get("freeway")
        direction = request.args.get("direction")
        stype     = request.args.get("type")

        query = {}
        if freeway:    query["freeway"]   = freeway
        if direction:  query["direction"] = direction
        if stype:      query["type"]      = stype

        docs = list(col.find(query, {"_id": 0, "location": 0}))
        return jsonify({"status": "ok", "count": len(docs), "stations": docs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
def api_stats():
    try:
        db  = get_db()
        col = db[COL_NAME]
        total = col.count_documents({})

        by_freeway = list(col.aggregate([
            {"$group": {"_id": "$freeway", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        by_type = list(col.aggregate([
            {"$group": {"_id": "$type", "count": {"$sum": 1}, "desc": {"$first": "$type_desc"}}},
            {"$sort": {"count": -1}}
        ]))
        return jsonify({"status": "ok", "total": total, "by_freeway": by_freeway, "by_type": by_type})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/freeways", methods=["GET"])
def api_freeways():
    try:
        db  = get_db()
        col = db[COL_NAME]
        freeways = sorted(col.distinct("freeway"))
        return jsonify({"status": "ok", "freeways": freeways})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/types", methods=["GET"])
def api_types():
    try:
        db  = get_db()
        col = db[COL_NAME]
        types = sorted(col.distinct("type"))
        return jsonify({"status": "ok", "types": types})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    for attempt in range(15):
        try:
            MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000).server_info()
            logger.info("MongoDB connected ✓")
            break
        except Exception as e:
            logger.warning(f"Waiting for MongoDB... ({attempt+1}/15)")
            time.sleep(2)

    try:
        col = get_db()[COL_NAME]
        if col.count_documents({}) == 0:
            logger.info("Empty collection – importing CSV …")
            load_csv_to_mongo()
        else:
            logger.info(f"Collection already has {col.count_documents({})} documents.")
    except Exception as e:
        logger.error(f"Auto-import failed: {e}")

    app.run(host="0.0.0.0", port=5000, debug=False)
