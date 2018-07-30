from nose import tools
from tests import test_app, user_data
from demo2.model import User
from demo2.common import util
from copy import deepcopy
import mongoengine
import json


class TestUser():
    @classmethod
    def setup_class(self):
        # 测试数据
        self.test_data = deepcopy(user_data)
        self.__test_save()
        self.__test_login()

    @classmethod
    def teardown_class(self):
        temp = User.objects(username='caihaoyu').first()
        if temp:
            temp.delete()

    @classmethod
    def __test_save(self):
        user = User(**self.test_data)
        user.password = util.md5(user.password)
        user.email = 'email'

        # user.save(
        with tools.assert_raises(mongoengine.errors.ValidationError):
            user = user.save()

        tools.assert_is_none(user.id)

        user = User(**self.test_data)
        user.password = util.md5(user.password)
        user.save()

        tools.assert_is_not_none(user.id)
        self.id = str(user.id)
        self.username = user.username
        self.password = self.test_data['password']
        # print(self.id, self.username, self.password)

    @classmethod
    def __test_login(self):
        # self.__test_save()
        test_user = {'username': self.username,
                     'password': self.password}
        test_user['password'] = self.password + '222'
        data = json.dumps(test_user)
        response = test_app.post('/api/v1/login',
                                 data=data,
                                 content_type='application/json')
        tools.assert_equals(response.status_code, 401)

        test_user['password'] = self.password
        data = json.dumps(test_user)
        response = test_app.post('/api/v1/login',
                                 data=data,
                                 content_type='application/json')

        tools.assert_equals(response.status_code, 200)
        json_resp = json.loads(response.data)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('access_token'))
        self.token = f'JWT {json_resp["data"]["access_token"]}'

    def test_me(self):
        headers = {'Authorization': self.token}
        response = test_app.get('/api/v1/user/me', headers=headers)
        tools.assert_equals(response.status_code, 200)
        json_resp = json.loads(response.data)

        user_data = json_resp.get('data')
        user = User.get_by_id(self.id)
        tools.assert_equals(user_data, user.api_response())
        tools.assert_is_none(user_data.get('password'))

        headers = {'Authorization': self.token + 'aaaa'}
        response = test_app.get('/api/v1/user/me')
        tools.assert_equals(response.status_code, 401)

        response = test_app.get('/api/v1/user/me', headers=headers)
        tools.assert_equals(response.status_code, 401)

    def test_post(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'aaa'
        t_data['email'] = 'yangxiaotong@geekpark.net'
        data = json.dumps(t_data)
        
        user = User.get_by_id(self.id)
        user.level = 1
        user.save()

        response = test_app.post('/api/v1/user',
                                 data=data,
                                 headers=headers,
                                 content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data).get('data'),
                            {'msg': "user don't has authority"})

        user.level = 9
        user.save()

        response = test_app.post('/api/v1/user',
                                 data=data,
                                 headers=headers,
                                 content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('id'))
        # User.get_by_id(self.uid).delete()
    
    def test_put(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'bbb'
        t_data['email'] = 'yangxiao@geekpark.net'
        t_data['password'] = 'test1'
        t_user = User(**t_data)
        t_user.save()
        data = json.dumps(t_data)

        user = User.get_by_id(self.id)
        user.level = 1 
        user.save()

        response = test_app.put(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 403)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Don\'t have authority'})
       
        user.level = 9
        user.save()

        t_data['username'] = 'ccc'
        data = json.dumps(t_data)
        response = test_app.put(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        tools.assert_equals(response.status_code, 403)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Can\'t modify username'})

        t_data['password'] = 'test2'
        t_data['username'] = 'bbb'
        data = json.dumps(t_data)
        response = test_app.put(f'/api/v1/user/{str(t_user.id)}',
                                data=data,
                                headers=headers,
                                content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        self.username = t_data.get('username')
        self.password = t_data.get('password')
        self.__test_login()

        # self.uid = json_resp.get('data').get('id')
        # # User.get_by_id(uid).delete()
    
    def test_delete(self):
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'ccc'
        t_data['email'] = 'yangxiao@geekpark.net'
        t_data['password'] = 'ccc'
        t_user = User(**t_data)
        t_user.save()

        user = User.get_by_id(self.id)

        response = test_app.delete(f'/api/v1/user/{str(t_user.id)}',
                                   headers=headers,
                                   content_type='application/json')
        tools.assert_equals(response.status_code, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'user don\'t has authority'})

        user.level = 9
        user.save()

        response = test_app.delete(f'/api/v1/user/{str(t_user.id)}',
                                   headers=headers,
                                   content_type='application/json')
        json_resp = json.loads(response.data)
        tools.assert_equals(response.status_code, 200)
        tools.assert_equals(json_resp.get('data'), 
                            {'msg': 'SUCCESS'})
 