"""Task CRUD endpoints — all protected by JWT, scoped to the current user."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_or_404(task_id: int, db: Session, user: models.User) -> models.Task:
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Create a new task for the authenticated user."""
    task = models.Task(**task_in.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=list[schemas.TaskRead])
def list_tasks(
    done: bool | None = Query(default=None, description="Filter by completion status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """List the authenticated user's tasks, optionally filtered by status."""
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    if done is not None:
        query = query.filter(models.Task.done == done)
    return query.order_by(models.Task.id).offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get a single task by id."""
    return _get_task_or_404(task_id, db, current_user)


@router.put("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Update a task (partial updates supported)."""
    task = _get_task_or_404(task_id, db, current_user)
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Delete a task."""
    task = _get_task_or_404(task_id, db, current_user)
    db.delete(task)
    db.commit()
    return None
