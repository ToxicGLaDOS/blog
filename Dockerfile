FROM python as build

RUN mkdir /blog
COPY . /blog/

WORKDIR /blog

RUN pip install -r requirements.txt && \
		python main.py

FROM nginx
COPY --from=build /blog/output/ /var/www/blog/
