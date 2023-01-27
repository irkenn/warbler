"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        
        # User should have no messages & no followers
        self.assertEqual(len(self.user.messages), 0)
        self.assertEqual(len(self.user.followers), 0)
    
    def test_repr(self):
        """Find if the representation matches"""
        
        self.assertIn(': testuser, test@test.com>', str(self.user))
    

    def test_is_following(self):
        """Detects when user 1 follows user 2"""
        
        user2 = User(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        db.session.add(user2)
        db.session.commit()

        """User 1 not following anyone"""
        
        self.assertEqual(len(self.user.followers), 0) 

        """User 2 not following User 1"""
        self.assertNotIn(self.user, user2.followers)


        """User 1 not following User 2"""
        self.assertNotIn(user2, self.user.followers)

        """User 1 is being followed by User 2"""
        follows = Follows(user_being_followed_id = self.user.id, user_following_id = user2.id)

        db.session.add(follows)
        db.session.commit()

        self.assertIn(user2, self.user.followers)
        self.assertIn(self.user, user2.following)
        
        """User 2 is being followed by User 1"""
        follows2 = Follows(user_being_followed_id = user2.id, user_following_id = self.user.id)

        db.session.add(follows2)
        db.session.commit()

        self.assertIn(user2, self.user.followers)
        self.assertIn(self.user, user2.following)

    
    def test_user_create(self):
        """Checks if the new user is created and also if it fails to create a user 
        with a duplicate username or email"""

        """With the correct credentials"""
        user2 = User.signup("testuser2", "test2@test2.com", "HASHED_PASSWORD2", "https://google.com")
        query1 = User.query.all()
        self.assertIn(user2, query1)


    def test_user_authenticate(self):
        """Tells if it returns a user when given a name and password"""
        
        User.signup("testuser2", "test2@test2.com", "HASHED_PASSWORD2", "https://google.com")

        """Check if True when the password is valid"""
        self.assertTrue(self.user.authenticate("testuser2", "HASHED_PASSWORD2"))
        
        """Check if False when the password is invalid"""
        self.assertFalse(self.user.authenticate("testuser2", "NOT_A_VALID_PASSWORD"))
    

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        """Create the user"""
        user1 = User.signup("testuser1", "test1@test1.com", "HASHED_PASSWORD1", "https://google.com")

        db.session.add(user1)
        db.session.commit()
        
        self.user = user1

        """Create a message"""
        message1 = Message(
            text="text&test",
            user_id= self.user.id
        )

        db.session.add(message1)
        db.session.commit()

        self.message = message1

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_message_content(self):
        """Check the representation of the message"""
        
        self.assertEqual('text&test', str(self.message.text))

    def test_owner_of_the_message(self):
        """Check that the id of the user that made the message is the same"""

        self.assertEqual(self.user.id, self.message.user_id)

    def test_create_new_message(self):
        """Check that the created message is in the database"""

        all_messages = Message.query.all()
        message2 = Message(text="text2&text2", user_id=self.user.id)
        """Check that the message is not in the database"""
        self.assertNotIn(message2, all_messages)
        
        """Add the message to the database"""
        db.session.add(message2)
        db.session.commit()
        """Make a new quer and check if the message is there"""
        all_messages = Message.query.all()
        self.assertIn(message2, all_messages)
    
    def test_delete_message(self):
        """Check that the selected message is out ot the database"""

        db.session.delete(self.message)
        all_messages = Message.query.all()
        self.assertNotIn(self.message, all_messages)
        




    















