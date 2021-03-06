from unittest import TestCase
from app import app
from models import db, User, DEFAULT_IMG_URL, Post, Tag, PostTag
import time, datetime

# Perform tests on a Test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):

    def setUp(self):
        """Delete any leftover database entries"""
        Post.query.delete()
        User.query.delete()
        Tag.query.delete()

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()
    
    def test_fullNameProp(self):
        user = User(first_name="John", last_name="Doe")
        self.assertEqual(user.full_name, "John Doe")

    def test_defaultImage(self):
        userOne = User(first_name="John", last_name="Doe")
        userTwo = User(first_name="Jane", last_name="Doe", image_url="https://duckduckgo.com/assets/bathroom.png")
        
        db.session.add(userOne)
        db.session.add(userTwo)
        db.session.commit()

        self.assertEqual(userOne.image_url, DEFAULT_IMG_URL)
        self.assertEqual(userTwo.image_url, "https://duckduckgo.com/assets/bathroom.png")

    def test_sortedQuery(self):
        userOne = User(first_name="John", last_name="Doe")
        userTwo = User(first_name="Jane", last_name="Doe")
        userThree = User(first_name="John", last_name="Fitzgerald")

        db.session.add_all([userOne, userTwo, userThree])
        db.session.commit()

        self.assertEqual(User.get_all(), [userTwo, userOne, userThree])

class PostModelTestCase(TestCase):
    def setUp(self):
        """Delete leftover DB entries and make a new entry, cache ID and timestamp"""
        Post.query.delete()
        User.query.delete()
        Tag.query.delete()
        
        user = User(first_name="John", last_name="Doe")
        db.session.add(user)
        db.session.commit()
        
        post = Post(title="My kitten", content="Look at my kitten, ain't she cute?", poster_id=user.id)
        db.session.add(post)
        db.session.commit()

        self.time_stamp = post.created_at
        self.user_id = user.id
    
    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_auto_timestamping(self):

        setup_post = Post.query.filter_by(title='My kitten').one()

        self.assertEqual(setup_post.created_at, self.time_stamp)

        time_marker = datetime.datetime.now()
        time.sleep(1)
        new_post = Post(title="My dog", content="Look at my dog, ain't he cute", poster_id=self.user_id)
        db.session.add(new_post)
        db.session.commit()

        self.assertNotEqual(time_marker, new_post.created_at)
        self.assertNotEqual(new_post.created_at, setup_post.created_at)

class PostTagModelTestCase(TestCase):

    def setUp(self):
        Post.query.delete()
        User.query.delete()
        Tag.query.delete()

        user = User(first_name="John", last_name="Doe")
        db.session.add(user)
        db.session.commit()
        
        post = Post(title="My kitten", content="Look at my kitten, ain't she cute?", poster_id=user.id)
        db.session.add(post)
        db.session.commit()

        tag1 = Tag(name="pets")
        tag2 = Tag(name="winning")

        db.session.add_all([tag1, tag2])
        db.session.commit()

        self.user_id = user.id
        self.post_id = post.id
        self.tag1_id = tag1.id
        self.tag2_id = tag2.id

    def tearDown(self):
        db.session.rollback()

    def test_posts_relationship(self):
        ## Adding
        post = Post.query.get(self.post_id)
        tag1 = Tag.query.get(self.tag1_id)
        tag2 = Tag.query.get(self.tag2_id)

        post.tags.append(tag1)
        post.tags.append(tag2)
        db.session.add(post)
        db.session.commit()

        self.assertIn(tag1, post.tags)
        self.assertIn(tag2, post.tags)

        ## Deletion cascade
        Tag.query.filter_by(id=self.tag1_id).delete()
        db.session.commit()

        self.assertNotIn(tag1, post.tags)
        self.assertIn(tag2, post.tags)