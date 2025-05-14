# Sử dụng Ubuntu 22.04 làm base image
FROM ubuntu:22.04

# Thiết lập biến môi trường để tránh các prompt tương tác khi cài đặt gói
ENV DEBIAN_FRONTEND=noninteractive

# Cập nhật danh sách gói và cài đặt Python 3 cùng pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements .

# Cài đặt các thư viện Python được liệt kê trong requirements.txt
RUN pip3 install --no-cache-dir -r requirements

# Sao chép toàn bộ mã nguồn ứng dụng vào container
COPY . .

# Khai báo rằng container sẽ lắng nghe trên cổng 7860
EXPOSE 7860

# Thiết lập biến môi trường để Gradio lắng nghe trên tất cả các giao diện mạng
ENV GRADIO_SERVER_NAME=0.0.0.0

# Thêm label cho Traefik
LABEL traefik.enable="true"
LABEL traefik.http.routers.shop.rule="Host(`test.svuit.org`) && PathPrefix(`/img2md`)"
LABEL traefik.http.services.shop.loadbalancer.server.port="7860"

# Lệnh chạy ứng dụng, thay 'index.py' bằng file chính của ứng dụng bạn
CMD ["python3", "api.py"]
