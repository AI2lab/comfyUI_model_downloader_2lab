import os.path
import zipfile
import subprocess
import traceback
import random
import requests
from tqdm import tqdm
from .constants import model_folder, models, custom_nodes_root, china_mirror
import platform
from torchvision.datasets.utils import download_url

# print("platform.system() = ", platform.system())

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
]

def download_model(node):
    custom_nodes_dirs = [name for name in os.listdir(custom_nodes_root) if os.path.isdir(os.path.join(custom_nodes_root, name)) and name != '__pycache__']

    # check nodes to download
    for key,value in models.items():
        if key in custom_nodes_dirs:
            if node!='' and node!=key: #如果指定了custom node，则只检查该custom node
                print("node = ",node)
                continue
            print(f"checking existed model file for {key}")
            for file in value['models']['files']:
                url = file['url']
                save_path = file['save_path']
                if 'save_path_2' in file:
                    save_path_2 = file['save_path_2']
                else:
                    save_path_2 = None
                node_save_path_2 = None
                filename = file['filename']
                if save_path.startswith('custom_nodes/'):
                    node_save_path = save_path.replace('custom_nodes/',"")
                    if save_path_2:
                        node_save_path_2 = save_path_2.replace('custom_nodes/',"")
                    if platform.system() == 'Windows':
                        node_save_path = node_save_path.replace('/','\\')
                        if node_save_path_2:
                            node_save_path_2 = node_save_path_2.replace('/','\\')
                    save_full_path = os.path.join(custom_nodes_root,node_save_path)
                    if node_save_path_2:
                        save_full_path_2 = os.path.join(custom_nodes_root,node_save_path_2)
                    else:
                        save_full_path_2 = None
                else:
                    if platform.system() == 'Windows':
                        save_path = save_path.replace('/','\\')
                        if save_path_2:
                            save_path_2 = save_path_2.replace('/','\\')
                    save_full_path = os.path.join(model_folder,save_path)
                    if save_path_2:
                        save_full_path_2 = os.path.join(model_folder,save_path_2)
                    else:
                        save_full_path_2 = None

                # print(f"save_full_path = {save_full_path}  ")
                file_path = os.path.join(save_full_path,filename)
                if os.path.exists(file_path):
                    print(f"{file_path} already exists")
                    continue
                elif save_full_path_2 and os.path.exists(os.path.join(save_full_path_2,filename)):
                    print(f"{file_path} already exists")
                    continue
                else:
                    print(f"{file_path} not exists")

                try:
                    # 如果模型文件不存在，启动下载
                    if not os.path.exists(save_full_path):
                        os.makedirs(save_full_path)
                    if china_mirror:
                        # huggingface 换成国内镜像站
                        if url.startswith('https://huggingface.co/'):
                            url = url.replace('https://huggingface.co/', 'https://hf-mirror.com/')
                    if url.startswith('https://huggingface.co/') or url.startswith('https://hf-mirror.com/'):
                        print("start download : ",filename)
                        success = download_huggingface_model_web(url,save_full_path,filename)

                        if success=='KeyboardInterrupt':
                            print_error("Keyboard Interrupt")
                            break
                        elif success=='fail':
                            print_error("download failed : "+url)
                            continue
                    else:
                        print("unsuppoted url : ",url)
                        continue
                except:
                    print("download file fail : ",url)
                    print(traceback.format_exc())


# torchvision.datasets.utils.download_url()，不支持断点续传
def download_huggingface_model_torchvision(url, save_full_path, filename) -> str:
    try:
        tempfilename = filename+".tempt"
        temp_file_path = os.path.join(save_full_path, tempfilename)
        file_path = os.path.join(save_full_path,filename)
        print("temp_file_path = ",temp_file_path)
        print("file_path = ",file_path)
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)

        download_url(url, temp_file_path)

        # 构建修改文件名的命令
        rename_command = [
            'mv',
            temp_file_path,
            file_path
        ]
        rename_process = subprocess.run(rename_command, check=True)

        # run unzip for zip file
        if filename.endswith('.zip'):
            unzip_command = ['unzip', file_path, '-d', save_full_path]
            unzip_process = subprocess.run(unzip_command, check=True)

        return 'success'
    except KeyboardInterrupt:
        print("命令执行被用户中断。")
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
        return 'KeyboardInterrupt'
    except subprocess.TimeoutExpired:
        print("命令执行超时。")
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
        return 'Fail'
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败，退出码：{e.returncode}")
        print(f"输出：{e.output}")
        print(f"错误输出：{e.stderr}")
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
        return 'Fail'
    except:
        print(traceback.format_exc())
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
        return 'Fail'

# wget，可以断点续传，但windows不带wget
def download_huggingface_model_wget(url, save_full_path, filename) ->str:
    try:
        tempfilename = filename+".tempg"
        temp_file_path = os.path.join(save_full_path, tempfilename)
        file_path = os.path.join(save_full_path,filename)

        wget_command = [
            'wget',
            '-c',
            '-O', temp_file_path,
            url
        ]
        print("wget command : ",wget_command)
        wget_process = subprocess.run(wget_command, check=True)

        # 构建修改文件名的命令
        rename_command = [
            'mv',
            temp_file_path,
            file_path
        ]
        rename_process = subprocess.run(rename_command, check=True)

        # run unzip for zip file
        if filename.endswith('.zip'):
            unzip_command = ['unzip', file_path, '-d', save_full_path]
            unzip_process = subprocess.run(unzip_command, check=True)

        return 'success'
    except KeyboardInterrupt:
        print("命令执行被用户中断。")
        return 'KeyboardInterrupt'
    except subprocess.TimeoutExpired:
        print("命令执行超时。")
        return 'Fail'
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败，退出码：{e.returncode}")
        print(f"输出：{e.output}")
        print(f"错误输出：{e.stderr}")
        return 'Fail'
    except:
        print(traceback.format_exc())
        return 'Fail'

# requests.get 可以断点续传
def download_huggingface_model_web(url, save_full_path, filename) ->str:
    try:
        tempfilename = filename+".temp"
        temp_file_path = os.path.join(save_full_path, tempfilename)
        file_path = os.path.join(save_full_path,filename)

        user_agent = random.choice(user_agents)
        resume_header = {
            'User-Agent': user_agent
        }

        file_mode = 'wb'
        resume_byte_pos = 0

        if os.path.exists(temp_file_path):
            resume_byte_pos = os.path.getsize(temp_file_path)
            resume_header = {'Range': f'bytes={resume_byte_pos}-'}
            file_mode = 'ab'

        response = requests.get(url, headers=resume_header, stream=True)
        total_size = int(response.headers.get('content-length', 0)) + resume_byte_pos

        with open(temp_file_path, file_mode) as file, tqdm(
                desc=temp_file_path,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                initial=resume_byte_pos,
                ascii=True,
                miniters=1
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

        # 修改文件名
        try:
            os.rename(temp_file_path, file_path)
        except OSError as e:
            print(f"rename failed: {e.strerror}")

        # run unzip for zip file
        if filename.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 解压缩所有内容到当前目录
                zip_ref.extractall(save_full_path)

        return 'success'
    except KeyboardInterrupt:
        print("命令执行被用户中断。")
        return 'KeyboardInterrupt'
    except subprocess.TimeoutExpired:
        print("命令执行超时。")
        return 'Fail'
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败，退出码：{e.returncode}")
        print(f"输出：{e.output}")
        print(f"错误输出：{e.stderr}")
        return 'Fail'
    except:
        print(traceback.format_exc())
        return 'Fail'

def execute_command(command, working_dir)->bool:
    try:
        # 执行Git命令
        print("execute_command : ",command)
        output = subprocess.run(command, cwd=working_dir, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, text=True)
        print(output.stdout)
        # print(output.decode('utf-8').strip())
        return True
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，打印错误信息
        print(f"Git command failed with error: {e.output.decode('utf-8').strip()}")
        return False



def print_console(text):
    print(f"\033[34m[INFO]\033[0m {text}")
def print_error(text):
    print(f"\033[31m[ERROR]\033[0m {text}")