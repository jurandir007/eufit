# EUFit/app/routers/social/routes.py
from flask import render_template, request, redirect, url_for, flash
from app.routers.social import social_bp
from app.routers.social.models import SocialUser, SocialPost, SocialComment, SocialLike, SocialFollow
from app.extensions import db
import sqlalchemy as sa


def get_social_engine():
    return db.engines.get("social") or db.engine


@social_bp.route("/")
def home():
    # Carrega posts com contagem de likes e comentários
    posts = (
        SocialPost.query
        .order_by(SocialPost.created_at.desc())
        .limit(30)
        .all()
    )
    users = SocialUser.query.order_by(SocialUser.username).all()
    
    # Métricas gerais do banco Social
    engine = get_social_engine()
    with engine.connect() as conn:
        total_posts = conn.execute(sa.text("SELECT COUNT(*) FROM posts")).scalar() or 0
        total_users = conn.execute(sa.text("SELECT COUNT(*) FROM users")).scalar() or 0
        total_likes = conn.execute(sa.text("SELECT COUNT(*) FROM likes")).scalar() or 0

    return render_template(
        "social/feed.html",
        posts=posts,
        users=users,
        total_posts=total_posts,
        total_users=total_users,
        total_likes=total_likes,
    )


@social_bp.route("/post/new", methods=["POST"])
def new_post():
    content = request.form.get("content", "").strip()
    user_id = request.form.get("user_id", type=int) or 1
    image_url = request.form.get("image_url", "").strip() or None

    if not content:
        flash("O conteúdo do post não pode estar vazio.", "error")
        return redirect(url_for("social.home"))

    post = SocialPost(
        user_id=user_id,
        content=content,
        image_url=image_url,
    )
    db.session.add(post)
    db.session.commit()
    flash("Post publicado com sucesso no ConnectHub!", "success")
    return redirect(url_for("social.home"))


@social_bp.route("/post/<int:post_id>/comment", methods=["POST"])
def new_comment(post_id):
    content = request.form.get("content", "").strip()
    user_id = request.form.get("user_id", type=int) or 1

    if not content:
        flash("O comentário não pode estar vazio.", "error")
        return redirect(url_for("social.home"))

    comment = SocialComment(
        post_id=post_id,
        user_id=user_id,
        content=content,
    )
    db.session.add(comment)
    db.session.commit()
    flash("Comentário adicionado!", "success")
    return redirect(url_for("social.home"))


@social_bp.route("/post/<int:post_id>/like", methods=["POST"])
def toggle_like(post_id):
    user_id = request.form.get("user_id", type=int) or 1
    existing = SocialLike.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Curtida removida.", "info")
    else:
        like = SocialLike(user_id=user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        flash("Você curtiu esta publicação!", "success")

    return redirect(url_for("social.home"))


@social_bp.route("/queries")
def queries_view():
    consultant_queries = [
        {
            "id": 1,
            "title": "Query 1: Timeline / Feed Personalizado (JOIN)",
            "requirement": "JOIN entre 2 ou mais tabelas (follows, users, posts)",
            "question": "Para a usuária 'ana_dev' (user_id = 1), quais são as postagens mais recentes publicadas pelas contas que ela segue?",
            "sql": """SELECT 
    u.username AS author_username,
    u.full_name AS author_name,
    p.post_id,
    p.content AS post_content,
    p.created_at AS published_at
FROM follows f
JOIN users u ON u.user_id = f.following_id
JOIN posts p ON p.user_id = u.user_id
WHERE f.follower_id = 1
ORDER BY p.created_at DESC
LIMIT 5;"""
        },
        {
            "id": 2,
            "title": "Query 2: Métricas Globais da Plataforma (Agregação)",
            "requirement": "Funções de agregação (COUNT, ROUND, NULLIF)",
            "question": "Qual é o total geral de postagens, curtidas, comentários e a média de engajamento por post?",
            "sql": """SELECT 
    COUNT(DISTINCT p.post_id) AS total_posts,
    COUNT(DISTINCT l.like_id) AS total_likes,
    COUNT(DISTINCT c.comment_id) AS total_comments,
    ROUND(COUNT(DISTINCT l.like_id)::NUMERIC / NULLIF(COUNT(DISTINCT p.post_id), 0), 2) AS avg_likes_per_post,
    ROUND(COUNT(DISTINCT c.comment_id)::NUMERIC / NULLIF(COUNT(DISTINCT p.post_id), 0), 2) AS avg_comments_per_post
FROM posts p
LEFT JOIN likes l ON l.post_id = p.post_id
LEFT JOIN comments c ON c.post_id = p.post_id;"""
        },
        {
            "id": 3,
            "title": "Query 3: Ranking de Popularidade de Autores (GROUP BY)",
            "requirement": "GROUP BY com ordenação agregada",
            "question": "Quais criadores de conteúdo acumularam o maior número de curtidas em seus posts?",
            "sql": """SELECT 
    u.user_id,
    u.username,
    u.full_name,
    COUNT(DISTINCT p.post_id) AS total_published_posts,
    COUNT(l.like_id) AS total_likes_received
FROM users u
JOIN posts p ON p.user_id = u.user_id
LEFT JOIN likes l ON l.post_id = p.post_id
GROUP BY u.user_id, u.username, u.full_name
ORDER BY total_likes_received DESC, total_published_posts DESC;"""
        },
        {
            "id": 4,
            "title": "Query 4: Posts Catalisadores de Debate (GROUP BY + HAVING)",
            "requirement": "GROUP BY combinado com HAVING",
            "question": "Quais publicações fomentaram debates na comunidade (receberam 2 ou mais comentários)?",
            "sql": """SELECT 
    p.post_id,
    u.username AS author,
    SUBSTRING(p.content, 1, 45) || '...' AS post_snippet,
    COUNT(c.comment_id) AS total_comments
FROM posts p
JOIN users u ON u.user_id = p.user_id
JOIN comments c ON c.post_id = p.post_id
GROUP BY p.post_id, u.username, p.content
HAVING COUNT(c.comment_id) >= 2
ORDER BY total_comments DESC, p.post_id ASC;"""
        },
        {
            "id": 5,
            "title": "Query 5: Grau de Influência e Conexões (Subquery / Escolha)",
            "requirement": "Query de escolha livre (Subqueries correlacionadas e filtros complexos)",
            "question": "Quais usuários possuem saldo social positivo (mais seguidores que seguindo) e qual a taxa de influência?",
            "sql": """SELECT 
    u.user_id,
    u.username,
    u.full_name,
    (SELECT COUNT(*) FROM follows WHERE following_id = u.user_id) AS total_followers,
    (SELECT COUNT(*) FROM follows WHERE follower_id = u.user_id)  AS total_following,
    ROUND(
        (SELECT COUNT(*) FROM follows WHERE following_id = u.user_id)::NUMERIC /
        NULLIF((SELECT COUNT(*) FROM follows WHERE follower_id = u.user_id), 0), 2
    ) AS influence_ratio
FROM users u
WHERE (SELECT COUNT(*) FROM follows WHERE following_id = u.user_id) >= 
      (SELECT COUNT(*) FROM follows WHERE follower_id = u.user_id)
ORDER BY total_followers DESC, influence_ratio DESC;"""
        },
        {
            "id": 6,
            "title": "Bônus: Identificação de Posts Virais (CTE / Week 9)",
            "requirement": "Common Table Expressions (WITH) e pontuação ponderada",
            "question": "Quais são os 3 posts com maior pontuação combinada de engajamento (Likes x1 + Comentários x2)?",
            "sql": """WITH PostEngagement AS (
    SELECT 
        p.post_id,
        p.user_id,
        p.content,
        COUNT(DISTINCT l.like_id) AS likes_count,
        COUNT(DISTINCT c.comment_id) AS comments_count,
        (COUNT(DISTINCT l.like_id) * 1 + COUNT(DISTINCT c.comment_id) * 2) AS engagement_score
    FROM posts p
    LEFT JOIN likes l ON l.post_id = p.post_id
    LEFT JOIN comments c ON c.post_id = p.post_id
    GROUP BY p.post_id, p.user_id, p.content
)
SELECT 
    pe.post_id,
    u.username AS author,
    pe.content AS post_text,
    pe.likes_count,
    pe.comments_count,
    pe.engagement_score
FROM PostEngagement pe
JOIN users u ON u.user_id = pe.user_id
ORDER BY pe.engagement_score DESC
LIMIT 3;"""
        }
    ]

    # Executa cada query ao vivo no banco Social
    engine = get_social_engine()
    results = []
    with engine.connect() as conn:
        for q in consultant_queries:
            res = conn.execute(sa.text(q["sql"]))
            columns = list(res.keys())
            rows = [list(row) for row in res.fetchall()]
            results.append({
                **q,
                "columns": columns,
                "rows": rows
            })

    return render_template("social/queries.html", results=results)
