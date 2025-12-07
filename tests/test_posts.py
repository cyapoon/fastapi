from typing import List
from app import schemas, models
import pytest

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200
    
def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401
    
def test_unauthorized_user_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401
    
def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/888")
    assert res.status_code == 404
    
def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    res_json = res.json()
    post = res_json['post']
    assert post['title'] == test_posts[0].title
    assert post['content'] == test_posts[0].content
    assert res.status_code == 200
    # assert post.Post
    
@pytest.mark.parametrize("title, content, published", [
    ("new title1", "new content1", True),
    ("new title2", "new content2", False),
    ("new title3", "new content3", True),
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post("posts/", json={"title": title, "content": content, "published": published})
    created_post = schemas.Post(**res.json())
    # print(created_post)
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']
    
def test_unauthorized_user_create_post(client, test_user, test_posts):
    res = client.post("/posts/", json={"title": "testing title", "content": "testing content"})
    assert res.status_code == 401
    
def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}/")
    assert res.status_code == 401
    
def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}/")
    assert res.status_code == 204

def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete("/posts/888/")
    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_user, test_user2, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[-1].id}/")
    assert res.status_code == 403
    
def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": 'updated content',
    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']
    
def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "updated title",
        "content": 'updated content',
    }
    res = authorized_client.put(f"/posts/{test_posts[-1].id}", json=data)
    assert res.status_code == 403
    
def test_unauthorized_user_update_post(client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": 'updated content',
    }
    res = client.put(f"/posts/{test_posts[0].id}/", json=data)
    assert res.status_code == 401
    
def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": 'updated content',
    }
    res = authorized_client.put("/posts/888/", json=data)
    assert res.status_code == 404