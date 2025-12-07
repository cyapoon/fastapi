from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, HTTPException, Response, status, Depends
from app import models, schemas, oauth2
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(prefix="/posts", tags=["Post"])

# @router.get("/sqlalchemy")
# async def test_posts(db: Session = Depends(get_db)):
#     posts = db.query(models.Post).all()
#     # print(posts)
#     return {"data": posts}

@router.get("/")
# @router.get("/", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user = Depends(get_current_user),
                    limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # print(results)
    return [{"Post": post, "votes": vote} for post, vote in results]
    

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                      current_user = Depends(get_current_user)):
    # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    
    new_post = models.Post(owner_id = current_user.id, **(post.model_dump()))
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# @router.get("/{id}", response_model=schemas.PostOut)
@router.get("/{id}")
async def get_post(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # cursor.execute("""select * from posts where id = %s""", (id,))
    # post = cursor.fetchone()
    # print(post)
    
    post = db.query(models.Post).filter(models.Post.id == id).first()
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.id == id).first()
    # print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post": post[0], "votes": post[1]}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
        
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not autherized to perform requested action.")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
async def update_post(id: int, update_post: schemas.PostCreate, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    # cursor.execute("update posts set title = %s, content = %s, published = %s where id = %s RETURNING *",
    #                (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()
    # if updated_post == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"post with id: {id} does not exist")
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not autherized to perform requested action.")
    post_query.update(update_post.model_dump(), synchronize_session=False)
    db.commit()
    
    return post_query.first()