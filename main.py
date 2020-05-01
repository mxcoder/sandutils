from io import BytesIO
from flask import Flask, request, Response

app = Flask(__name__, static_url_path='', static_folder='./static')

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/v1/pivot', methods=['POST'])
def pivot():
    from pivot_site_survey.main import writeBook, main as pivoter

    f = request.files['file']
    df = pivoter(f.stream)

    output = BytesIO()
    writeBook(df, output)
    output.seek(0)

    return Response(
        output,
        mimetype="application/vnd.ms-excel",
        headers={"Content-disposition": "attachment; filename=pivoted.xls"})


@app.route('/v1/neighbours', methods=['POST'])
def neighbours():
    from neighbours_match.main import writeBook, main as matcher

    f_gsm = request.files['gsm']
    f_lte = request.files['lte']
    f_umts = request.files['umts']
    sheets = matcher(f_gsm, f_lte, f_umts)

    output = BytesIO()
    writeBook(sheets, output)
    output.seek(0)

    return Response(
        output,
        mimetype="application/vnd.ms-excel",
        headers={"Content-disposition": "attachment; filename=neighbours.xls"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
