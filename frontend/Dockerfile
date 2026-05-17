FROM node:20-slim

# Next.jsのホットリロードがコンテナ内で確実に検知できるように環境変数を設定
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"
ENV WATCHPACK_POLLING true

WORKDIR /workspace

# 開発環境なので、パッケージのインストールなどは
# マウントしたローカルの package.json を見てコンテナ起動時に行うか、
# もしくはこのまま起動してローカルと同期させます