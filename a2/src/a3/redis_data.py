# brew services start redis
import redis
from flask import Flask, request, render_template_string
from lsh import nearest_neighbor_search

r = redis.Redis(host="lsh-redis-data", port=6379, db=0)
app = Flask(__name__)

# the output got printed on http://127.0.0.1:5001


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and "query" in request.form:
        try:
            query_text = request.form["query"]
            filename = request.form["filename"]
            # Call nearest neighbor search METHOD
            result = nearest_neighbor_search(
                file_path=f"/app/src/a3/data/{filename}",
                redis_key_prefix=filename,
                query=query_text,
                num_hashes=300,
                num_bands=50,
                rows_per_band=2,
            )
            # stored_data = []
            # keys = r.keys(f"{filename}:*")
            # if not keys:
            #     return "<h1>Error: No data found in Redis</h1>"

            # for key in keys:
            #     value = r.get(key)
            #     if value is None:
            #         continue
            #     stored_data.append(f"{key} => {value.decode('utf-8')}")

            return render_template_string(
                """
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; text-align: center; flex-direction: column; position: relative;">
                    <h1 style="font-size: 36px;">Nearest Neighbor Search Result:</h1>
                    <p style="font-size: 25px; color: blue">{{ result }}</p>
                    <a href="/" style="position: absolute; bottom: 20px; right: 20px; font-size: 16px; text-decoration: none; background-color: #007bff; color: white; padding: 10px 15px; border-radius: 5px;">Back to Home</a>
                </div>
                """,
                result=result,
            )
        except FileNotFoundError:
            return """
                <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; text-align: center; position: relative;">
                    <h1 style="font-size: 36px; color: red;">File not found. Please make sure the file exists in the data directory.</h1>
                    <a href="/" style="position: absolute; bottom: 20px; right: 20px; font-size: 16px; text-decoration: none; background-color: #007bff; color: white; padding: 10px 15px; border-radius: 5px;">Back to Home</a>
                </div>
                """
        except Exception as e:
            return f'<h1 style="font-size: 36px; color: red; margin-bottom: 20px;">Error processing file: {str(e)}</h1>'

    return render_template_string(
        """
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; text-align: center;">
                <h1 style="font-size: 36px; margin-bottom: 20px;">Enter the filename and query for LSH Near Neighbor Search:</h1>
                <form method="POST" style="width: 50%; max-width: 600px; text-align: left;">
                    <label for="filename" style="font-size: 18px; margin-bottom: 10px; display: block;">Enter filename (e.g., <code>five.tsv</code>):</label>
                    <input type="text" id="filename" name="filename" required style="width: 100%; padding: 10px; margin-bottom: 20px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px;">
                    
                    <label for="query" style="font-size: 18px; margin-bottom: 10px; display: block;">Enter query (e.g., <code>"TWO CHERRY PUMPKIN TARTS"</code>):</label>
                    <input type="text" id="query" name="query" required style="width: 100%; padding: 10px; margin-bottom: 20px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px;">
                    
                    <div style="text-align: center;">
                        <button type="submit" style="font-size: 16px; padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Submit</button>
                    </div>
                </form>
            </div>
            """
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Makes the server accessible externally

#  * Running on all addresses (0.0.0.0)
#  * Running on http://127.0.0.1:5001
#  * Running on http://172.19.0.3:5001
# Press CTRL+C to quit
