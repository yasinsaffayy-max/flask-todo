import app as app_module


class TestHomePage:
    """تست صفحه اصلی"""

    def test_home_loads(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_home_shows_no_tasks_message(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_home_with_tasks(self, client, sample_tasks):
        r = client.get('/')
        assert r.status_code == 200
        assert 'خرید نان'.encode() in r.data
        assert 'تمیز کردن خانه'.encode() in r.data


class TestAddTask:
    """تست افزودن تسک"""

    def test_add_valid_task(self, client):
        r = client.post('/add', data={'task': 'خرید شیر'}, follow_redirects=True)
        assert r.status_code == 200
        assert len(app_module.tasks) == 1
        assert app_module.tasks[0]['title'] == 'خرید شیر'
        assert app_module.tasks[0]['done'] is False

    def test_add_empty_task(self, client):
        """تسک خالی نباید اضافه بشه"""
        client.post('/add', data={'task': ''})
        assert len(app_module.tasks) == 0

    def test_add_missing_field(self, client):
        client.post('/add', data={})
        assert len(app_module.tasks) == 0

    def test_add_whitespace_task(self, client):
        """فقط فاصله هم قبول نکن (تسک فعلی)"""
        client.post('/add', data={'task': '   '})
        # کد فعلی اینو قبول می‌کنه، پس تسک اضافه می‌شه
        assert len(app_module.tasks) == 1

    def test_add_multiple_tasks(self, client):
        client.post('/add', data={'task': 'تسک اول'})
        client.post('/add', data={'task': 'تسک دوم'})
        client.post('/add', data={'task': 'تسک سوم'})
        assert len(app_module.tasks) == 3

    def test_add_generates_unique_ids(self, client):
        client.post('/add', data={'task': 'a'})
        client.post('/add', data={'task': 'b'})
        client.post('/add', data={'task': 'c'})
        ids = [t['id'] for t in app_module.tasks]
        assert len(ids) == len(set(ids))

    def test_add_redirects(self, client):
        r = client.post('/add', data={'task': 'test'})
        assert r.status_code == 302


class TestToggleDone:
    """تست علامت زدن انجام‌شده"""

    def test_toggle_not_done_to_done(self, client, sample_tasks):
        assert app_module.tasks[0]['done'] is False
        client.get('/done/1')
        assert app_module.tasks[0]['done'] is True

    def test_toggle_done_to_not_done(self, client, sample_tasks):
        assert app_module.tasks[1]['done'] is True
        client.get('/done/2')
        assert app_module.tasks[1]['done'] is False

    def test_toggle_twice_returns_to_original(self, client, sample_tasks):
        client.get('/done/1')
        client.get('/done/1')
        assert app_module.tasks[0]['done'] is False

    def test_toggle_nonexistent_id(self, client, sample_tasks):
        """ID ناموجود نباید خطا بده"""
        r = client.get('/done/999', follow_redirects=True)
        assert r.status_code == 200
        # tasks دست‌نخورده بمونه
        assert len(app_module.tasks) == 3

    def test_toggle_redirects(self, client, sample_tasks):
        r = client.get('/done/1')
        assert r.status_code == 302


class TestDeleteTask:
    """تست حذف تسک"""

    def test_delete_existing_task(self, client, sample_tasks):
        assert len(app_module.tasks) == 3
        client.get('/delete/1')
        assert len(app_module.tasks) == 2
        assert all(t['id'] != 1 for t in app_module.tasks)

    def test_delete_nonexistent_id(self, client, sample_tasks):
        client.get('/delete/999')
        assert len(app_module.tasks) == 3

    def test_delete_all_tasks(self, client, sample_tasks):
        client.get('/delete/1')
        client.get('/delete/2')
        client.get('/delete/3')
        assert len(app_module.tasks) == 0

    def test_delete_redirects(self, client, sample_tasks):
        r = client.get('/delete/1')
        assert r.status_code == 302


class TestIntegration:
    """تست سناریوهای ترکیبی"""

    def test_full_workflow(self, client):
        # 1. یه تسک اضافه کن
        client.post('/add', data={'task': 'کار مهم'})
        assert len(app_module.tasks) == 1
        task_id = app_module.tasks[0]['id']

        # 2. انجامش بده
        client.get(f'/done/{task_id}')
        assert app_module.tasks[0]['done'] is True

        # 3. حذفش کن
        client.get(f'/delete/{task_id}')
        assert len(app_module.tasks) == 0

    def test_multiple_operations(self, client):
        for i in range(5):
            client.post('/add', data={'task': f'تسک {i}'})
        assert len(app_module.tasks) == 5

        client.get('/done/1')
        client.get('/done/3')
        client.get('/done/5')

        done_count = sum(1 for t in app_module.tasks if t['done'])
        assert done_count == 3

        client.get('/delete/2')
        assert len(app_module.tasks) == 4
