import datetime
from demo2 import rest_api
from flask_restful import reqparse
from flask import request
from flask_jwt import jwt_required

from demo2.service.user import get_current_user, rule_required
from demo2.api.base import BaseAPI
from demo2.model.article import Article
from demo2.model.user import User
from demo2.common import util

parser = reqparse.RequestParser()


@rest_api.route('/api/v1/article', endpoint='article')
@rest_api.route('/api/v1/article/<string:id>', endpoint='article_detail')
class ArticleAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        """
        @api {get} /article/:id 获取原生文章列表
        @apiName articlelist
        @apiGroup articlelist
        @apiDescription 查询未编辑的文章列表
        @apiVersion 1.0.0

        @apiParam {Integer} [page_size] 每页条数
        @apiParam {Integer} [page] 页数
        """
        if id:
            articles = Article.get_by_id(id=id)
            return util.api_response(data=articles.api_response())
        else:
            parser.add_argument('page_size', type=int, default=20)
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('order_by', type=str, default='-added')
            args = parser.parse_args()
            page_size = args.get('page_size')
            page = args.get('page')
            order_by = [args.get('order_by')]
            query = {}

            result = util.paging(
                cls=Article,
                page=page,
                query=query,
                page_size=page_size,
                order_by=order_by
            )

            return util.api_response(data=result)

    @jwt_required()
    @rule_required()
    def post(self):
        """
        @api {get} /article 新增文章
        @apiName articlelist
        @apiGroup articlelist
        @apiDescription 保存文章到article数据库       
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "title":"hhhhh",
            "url":"fdsafdsf.net"
        }

        @apiParam {Integer} [page_size] 每页条数
        @apiParam {Integer} [page] 页数
        """
        data = request.get_json(force=True)
        data['added'] = datetime.datetime.now()

        if data.get('author'):
            user = User.get_by_id(data.get('author'))
            data['author'] = user
        else:
            data['author'] = get_current_user()
    
        articles = Article(**data).save()
        articles.author.save()

        if articles:
            return util.api_response(articles.api_response())
        else:
            raise ValueError('save failure')

    @jwt_required()
    @rule_required()
    def put(self, id=None):
        """
        @api {put} /v1/user 修改article
        @apiName user
        @apiGroup user
        @apiDescription 修改article
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "title":"hhhhh",
            "url":"fdsafdsf.net"
        }

        @apiErrorExample {json} Error-Response:
            HTTP/1.1 500 ERROR
            {
                "msg": "File not found"
            }
        """
        if id is None:
            raise ValueError('id not found')
        data = request.get_json(force=True)
        print(data)
        articles = Article.objects.get(id=id)
      
        if data.get('author'):
            user = User.get_by_id(data.get('author'))
            
            data['author'] = user
        else:
            data['author'] = get_current_user()
            
        if articles:
            articles.update(**data)
            articles.reload()
            return util.api_response(data=articles.api_response())
        else:
            raise ValueError('save failure')

    @jwt_required()
    @rule_required()
    def delete(self, id=None):
        if id is None:
            raise ValueError('id not found')
        articles = Article.get_by_id(id)
        articles.delete() 
        return util.api_response(data={'msg': 'SUCCESS'})
