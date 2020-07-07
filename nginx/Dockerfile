FROM nginx:1.19

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
COPY cvpr.conf /etc/nginx/conf.d/