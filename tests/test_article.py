from nose import tools
from tests import test_app, user_data, article_data, BaseTest
from demo2.model import User, Article
from copy import deepcopy
import json


class TestArticle(BaseTest):
    @classmethod
    def setup_class(self):
        # 测试数据
        self.test_data1 = deepcopy(user_data)
        self.test_data2 = deepcopy(article_data)
        self.test_data1['username'] = 'yangminngli'
        self.test_data1['level'] = 9
        self.article_data = deepcopy(article_data)
        self.article_id_list = []
        self.test_login(self.test_data1)
        self.__test_save_article()

    @classmethod
    def teardown_class(self):
        User.objects().delete()
        for id in self.article_id_list:
            articles = Article.objects(id=id).first()
            if articles:
                articles.delete()

    @classmethod
    def __test_save_article(self):
        for i in range(25):
            articles = Article(**self.article_data)
            articles.url = articles.url + str(i)
            articles.author = self.user
            articles.save()
            self.article_id_list.append(articles.id)
            self.user_id = self.user.id
        
    @tools.nottest
    def test_paging(self, response, page, page_size=20):
        json_resp = self.validate_response(response)
        article = Article.objects()
        length = len(article)
        list_len = page_size

        tools.assert_equals(json_resp['data']['page_sum'], length//20+1)
        if page == json_resp['data']['page_sum']:
            list_len = length % page_size
            if list_len == 0:
                list_len = 20

        tools.assert_equals(len(json_resp['data']['list']), list_len)

        tools.assert_equals(json_resp['data']['count'], length)
        tools.assert_equals(json_resp['data']['current_page'], page)

        if page == 1:
            tools.assert_equals(json_resp['data']['list'][0].get(
                'id'), str(self.article_id_list[0]))

    def test_article_paging(self):
        headers = {'Authorization': self.token}
        print(len(self.article_id_list))
        response = test_app.get('/api/v1/article', headers=headers)
        self.test_paging(response, 1)

        headers = {'Authorization': self.token}
        response = test_app.get('/api/v1/article?page=2&page_size=20',
                                headers=headers)
        self.test_paging(response, 2)

    def test_article_get(self):
        headers = {'Authorization': self.token}
        test_article = Article.get_by_id(self.article_id_list[1])
        url = f'/api/v1/article/{str(self.article_id_list[1])}'
        response = test_app.get(url, headers=headers)
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp['data'])
        tools.assert_equals(json_resp['data'], test_article.api_response())
    
    def test_article_post(self):
        """
        测试edited_article的post接口
        1、测试登录认证
        2、测试权限问题，普通用户不能提交
        """
        headers = {'Authorization': self.token + 'aaaa'}
        response = test_app.post('/api/v1/article')
        tools.assert_equals(response.status_code, 401)
        response = test_app.post('/api/v1/article', headers=headers)
        tools.assert_equals(response.status_code, 401)

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data2)
        t_data.pop('added')
        data = json.dumps(t_data)

        user = User.get_by_id(self.user_id)
        user.level = 1
        user.save()

        response = test_app.post('/api/v1/article',
                                 data=data,
                                 headers=headers,
                                 content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': "user don't has authority"})

        user.level = 9
        user.save()

        response = test_app.post('/api/v1/article',
                                 data=data,
                                 headers=headers,
                                 content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('id'))

    def test_article_put(self):
        """
        测试edited_article的put接口
        1、测试登录认证
        2、测试权限问题，普通用户不能提交
        """

        user = User.get_by_id(self.user_id)
        user.level = 1
        user.save()

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data2)
        t_user_data = deepcopy(self.test_data1)
        t_article = Article.get_by_id(str(self.article_id_list[0]))

        t_user_data['username'] = 'ccc'
        t_user_data['email'] = 'ccc@geekpark.net'
        t_user = User(**t_user_data)
        t_user.save()

        t_data['author'] = str(t_user.id)
        t_data.pop('added')
        data = json.dumps(t_data)

        response = test_app.put(f'/api/v1/article/{str(t_article.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'user don\'t has authority'})

        user = User.get_by_id(self.user_id)
        user.level = 9
        user.save()

        response = test_app.put(f'/api/v1/article/{str(t_article.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('id'))
        t_user.delete()

    def test_article_delete(self):
        """
        测试edited_article的delete接口
        1、测试登录认证
        2、测试权限问题，普通用户不能提交
        """

        user = User.get_by_id(self.user_id)
        user.level = 1
        user.save()

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data2)
        t_user_data = deepcopy(self.test_data1)
        t_article = Article.get_by_id(str(self.article_id_list[-1]))
        
        t_user_data['username'] = 'bbb'
        t_user_data['email'] = 'yangxiao@geekpark.net'
        t_user = User(**t_user_data)
        t_user.save()

        t_data['author'] = str(t_user.id)
        t_data.pop('added')
        data = json.dumps(t_data)

        response = test_app.delete(f'/api/v1/article/{str(t_article.id)}',
                                   data=data,
                                   headers=headers,
                                   content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'user don\'t has authority'})

        user = User.get_by_id(self.user_id)
        user.level = 9
        user.save()

        response = test_app.delete(f'/api/v1/article/{str(t_article.id)}',
                                   data=data,
                                   headers=headers,
                                   content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        t_user.delete()
