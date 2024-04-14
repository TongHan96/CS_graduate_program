import pandas as pd
from flask import Flask, request, redirect, render_template_string, jsonify, send_file
from io import BytesIO
import os
from code_1 import extraction, detection, fuzzy_match

##### Func
def handle_extraction(file, model_engine, api_key):
    data_df1, data_df2 = extraction(file, model_engine, api_key)
    df1 = pd.DataFrame(data_df1)
    df2 = pd.DataFrame(data_df2)
    print(df1)
    print(df2)
    df1['因子意义'] = df1['因子'].apply(lambda x: fuzzy_match(x, df2))
    return df1

def handle_detection(file, model_engine, api_key):
    data_df1, data_df2 = detection(file, model_engine, api_key)
    df1 = pd.DataFrame(data_df1)
    df2 = pd.DataFrame(data_df2)
    print(df1)
    print(df2)
    df1['因子意义'] = df1['因子'].apply(lambda x: fuzzy_match(x, df2))
    df1.columns = ['问题','因子','因子意义']
    return df1


def get_html_file(filename, content_to_display):
    html = f'''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #FFFFFF; 
        }}
    .container {{
        max-width: 800px;
        margin: auto;
        background: #FFFFFC;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.6);
        border-radius: 20px; 
        border: 1px solid #ccc; 
    }}
    .title {{
        text-align: center;
        color: #333;
    }}
    .side-by-side {{
        display: flex;
        justify-content: space-between;
    }}
    .section {{
        flex: 1;
        padding: 10px; /* Adjust padding as needed */
    }}
    img {{
        max-width: 100%; /* Adjust based on actual content */
        height: auto;
        margin: 10px 0;
    }}
    a {{
        display: block;
        text-decoration: none;
        background-color: #007bff;
        color: #FFFFFF;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 20px auto;
        width: fit-content;
    }}
    a:hover {{
        background-color: #0056b3;
    }}
    .table {{
        width: 100%;
        margin-bottom: 1rem;
        color: #212529;
    }}
    .table-striped tbody tr:nth-of-type(odd) {{
        background-color: rgba(0,0,0,.05);
    }}
    .table th {{
        text-align: center; /* Center align table headers */
    }}
    </style>
    </head>
    <body>
    <div class="container">
        <h3>您已经成功读取了{filename}，下面是量表操作结果展示！</h3>
        <div class="content">
            {content_to_display}
        </div>
        <div class="button-container">
            <a href="/upload" class="btn btn-primary">继续上传</a>
            <a href="/" class="btn btn-secondary">回到首页</a>
            <a href="/download/{filename}" class="btn btn-success">下载文件</a>
        </div>
    </div>
    </body>
    </html>
    '''
    return html


def get_html_file2(filename, content_to_display):
    html = f'''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
            body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #FFFFFF; 
        }}
    .container {{
        max-width: 800px;
        margin: auto;
        background: #FFFFFC;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.6);
        border-radius: 20px; 
        border: 1px solid #ccc; 
    }}
    .title {{
        text-align: center;
        color: #333;
    }}
    .side-by-side {{
        display: flex;
        justify-content: space-between;
    }}
    .section {{
        flex: 1;
        padding: 10px; /* Adjust padding as needed */
    }}
    img {{
        max-width: 100%; /* Adjust based on actual content */
        height: auto;
        margin: 10px 0;
    }}
    a {{
        display: block;
        text-decoration: none;
        background-color: #007bff;
        color: #FFFFFF;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 20px auto;
        width: fit-content;
    }}
    a:hover {{
        background-color: #0056b3;
    }}
    .table {{
        width: 100%;
        margin-bottom: 1rem;
        color: #212529;
    }}
    .table-striped tbody tr:nth-of-type(odd) {{
        background-color: rgba(0,0,0,.05);
    }}
    .table th {{
        text-align: center; /* Center align table headers */
    }}
    </style>
    </head>
    <body>
    <div class="container">
        <h3>您已经成功上传了{filename}，下面是操作结果展示！</h3>
        <div class="content">
            {content_to_display}
        </div>
        <div class="button-container">
            <a href="/upload" class="btn btn-primary">继续上传</a>
            <a href="/" class="btn btn-secondary">回到首页</a>
        </div>
    </div>
    </body>
    </html>
    '''     
    return html  


#### App
app = Flask(__name__)
save_path2 = os.path.join(app.root_path, 'uploads')
# Configure the upload folder; make sure this path exists and is writable
app.config['UPLOAD_FOLDER'] = 'uploads'  # Make sure this directory exists

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return '''
   <!DOCTYPE html>
    <html lang="zh">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>量表知识抽取工具</title>
    <style>
            body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #FFFFFF; /* Change the background color here */
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: #FFFFFC;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.6);
            border-radius: 20px; /* Add border radius */
            border: 1px solid #ccc; /* Add border */
        }
        .title {
            text-align: center;
            color: #333;
        }
        .images {
            display: flex;
            justify-content: space-around;
            align-items: center;
        }
        img {
            max-width: 48%;
            height: auto;
            margin: 10px 0;
        }
        a {
            display: block;
            text-decoration: none;
            background-color: #007bff;
            color: #FFFFFF;
            padding: 10px 20px;
            border-radius: 5px;
            margin: 20px auto;
            width: fit-content;
        }
        a:hover {
            background-color: #0056b3;
        }
    </style>
    </head>
    <body>
    <div class="container">
        <h1 class="title">基于GPT的交互式量表知识抽取工具</h1>
        <div class="images">
            <img src="https://image12.bookschina.com/2015/20150502/7051263.jpg" alt="量表示例图">
            <img src="https://blackbox.com.sg/wp-content/uploads/2023/03/GPT-4-Is-Here.png" alt="GPT-4介绍图">
        </div>
        <h3>本课题是“量表资源语义互联”项目的组成部分。临床量表是大量临床实践过程中总结出的一般性工具，是现代临床工作人员不可缺少的“工具箱”。随着临床医学各学科理论基础不断成熟和测量技术持续改善，临床量表的数量已达到相当大的规模。同时，现有量表的修订、不断编制的新量表出现。这使得临床量表知识获取与学习成本变得较高，阻碍了量表在临床中的应用。</h3>
        <p><a href="/upload">上传新文件</a></p>
    </div>
    </body>
    </html>
    '''


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    show_container = False
    if request.method == 'POST':
        if "ext_det" in request.form:
            show_container = True
        elif 'model_engine' in request.form and 'api_key' in request.form:
            model_engine = request.form['model_engine']
            api_key = request.form['api_key']
            print("Model Engine:", model_engine)
            print("API Key:", api_key)

        # 仍未上传文件，则重定向
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = file.filename
            df1 = pd.read_excel(file, header=None)
            df2 = pd.read_excel(file, sheet_name='Sheet2', header=None)
            df1.columns = ['问题项','因子']
            df2.columns = ['因子及映射']
            first_rows1 = df1.head().to_html(classes='table table-striped', index=False, border=1)
            first_rows2 = df2.head().to_html(classes='table table-striped', index=False, border=1)
            content_to_display = first_rows1 + first_rows2  # Default content
            file.save(os.path.join(save_path2, filename))
            
        if "extraction" in request.form and 'model_engine' in request.form and 'api_key' in request.form:
            message = handle_extraction(file, model_engine=model_engine, api_key=api_key) 
            operation = "量表提取"
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                message.to_excel(writer, index=False)
            output.seek(0)
            full_save_path = os.path.join(save_path2, filename)
            with open(full_save_path, 'wb') as f:
                f.write(output.read())
            content_to_display = message.to_html(classes='table table-striped', index=False, border=1)
            html = get_html_file(filename, content_to_display)
            return render_template_string(html)

        elif 'detection' in request.form and 'model_engine' in request.form and 'api_key' in request.form:
            prompt_text = handle_detection(file, model_engine=model_engine, api_key=api_key)  # Define this function to handle detection
            operation = "量表发现"
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                prompt_text.to_excel(writer, index=False)
            output.seek(0)
            full_save_path = os.path.join(save_path2, filename)
            with open(full_save_path, 'wb') as f:
                f.write(output.read())
            content_to_display = prompt_text.to_html(classes='table table-striped', index=False, border=1)
            html = get_html_file(filename, content_to_display)
            return render_template_string(html)
        
        elif "checking" in request.form:
            html = get_html_file2(filename, content_to_display)
            return render_template_string(html)
  
    tmp_html = '''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上传文件</title>
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f0f2f5;
        margin: 0;
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    .wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .container {
        background-color: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        width: 500px;
        margin-bottom: 20px;
    }
    .title {
        color: #333;
        text-align: center;
    }
    .upload-section {
        margin-top: 20px;
    }
    form {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    input[type="file"] {
        border: 1px solid #ccc;
        display: block;
        padding: 6px;
        width: 100%;
    }
    input[type="submit"] {
        background-color: #4CAF50;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    input[type="submit"]:hover {
        background-color: #45a049;
    }
    input[type="text"] {
        padding: 8px;
        width: 100%;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    input[type="file"], input[type="text"], input[type="password"] {
        border: 1px solid #ccc;
        padding: 6px;
        width: 100%;
        border-radius: 4px;
    }
    label {
        font-size: 14px;
        color: #333;
    }
    </style>
    </head>
    <body>
    <div class="container">
        <h1 class="title">上传文件</h1>
        <h3>请上传医学量表&因子及其映射文件。如果您需要进行量表提取和发现，请同时提供您所需的GPT模型引擎及API密钥。</h3>
        <div class="upload-section">
                <form method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" id="checking" name="checking" value="量表查看">
                <div style="height: 20px;"></div> <!-- added space -->
                <label for="model_engine">模型引擎:</label>
                <input type="text" id="model_engine" name="model_engine"><br>
                <label for="api_key">OpenAI API Key:</label>
                <input type="password" id="api_key" name="api_key"><br> 
                <input type="submit" id="extraction" name="extraction" value="量表提取">
                <input type="submit" id="detection" name="detection" value="量表发现">                
                </form>
        </div>
    </div>
    <p><a href="/">回到首页</a></p>
    </body>
    </html>
    '''
    return render_template_string(tmp_html, show_container=show_container)

@app.route('/download/<filename>')
def download_file(filename):
    # Assuming 'save_path2' is defined elsewhere and points to the directory where your files are stored.
    path_to_file = os.path.join(save_path2, filename)
    try:
        return send_file(path_to_file, as_attachment=True, download_name=filename)
    except Exception as e:
        return str(e)  # Or handle the error as you see fit