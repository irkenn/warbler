"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows
from flask import Flask, session

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                email="tes2t@test2.com",
                                password="testuser2",
                                image_url=None)

        self.testuser3 = User.signup(username="testuser3",
                                email="tes3t@test3.com",
                                password="testuser3",
                                image_url=None)

        

        db.session.commit()

        #arrangement following 1 -> 2 -> 3 -> 1
        #arrangement followers 1 -> 3 -> 2 -> 1
        following1 = Follows(user_being_followed_id=self.testuser2.id,
                                user_following_id=self.testuser.id)
        following2 = Follows(user_being_followed_id=self.testuser3.id,
                                user_following_id=self.testuser2.id)
        following3 = Follows(user_being_followed_id=self.testuser.id,
                                user_following_id=self.testuser3.id)
        
        
        db.session.add_all([following1, following2, following3])
        db.session.commit()

        self.following1 = following1
        self.following2 = following2
        self.following3 = following3
        

        

    def tearDown(self):
        """Cleans fouled transactions"""

        db.session.rollback()

    def test_add_and_delete_message_as_user(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            """Add messages as user"""
            resp = c.post("/messages/new", data={"text": "Hello"})
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

            """Check the user is the owner of the message"""
            self.assertEqual(msg.user_id, self.testuser.id)

            """Delete messages as user"""
            resp2 = c.post(f'/messages/{msg.id}/delete')
            self.assertEqual(resp2.status_code, 302)
            #Check the result is None
            msg = Message.query.one_or_none()
            self.assertIsNone(msg)


    def test_add_and_delete_message_logout(self):
        """Can we add or delete a message while being logged out?"""

        with app.test_client() as c:

            """Add messages without loggin in"""
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertIn("Access unauthorized.", html)
            #check the message was not added
            msg = Message.query.one_or_none()
            self.assertIsNone(msg)

            """Add messages without loggin in"""
            resp2 = c.post(f'/messages/1/delete', follow_redirects=True)
            html2 = resp2.get_data(as_text=True) 
            self.assertIn("Access unauthorized.", html2)

    
    def test_show_following_followers(self):
        """Check that it shows the following and followers"""
        
        # with app.test_client() as c:
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            
            #arrangement following 1 -> 2 -> 3 -> 1
            #arrangement followers 1 -> 3 -> 2 -> 1

            """Check that user 1 is following user2"""
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertIn("testuser2", html)
        
            """Check that user 1 is being followed by user 3"""
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertIn("testuser3", html)

            """Check that user 1 is not following user 3"""
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertNotIn("testuser3", html)          
            
            """Check that user 1 is not being followed by user 2"""
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertNotIn("testuser2", html)


    def test_not_showing_following_followers_logout(self):
        """Check that it shows the following and followers"""
        
        with app.test_client() as c:

            """While logged out check following page"""
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertIn("Access unauthorized.", html)

            """While logged out check followers page"""
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True) 
            self.assertIn("Access unauthorized.", html)
    
    def add_message_as_other_user(self):
        """Check that only the current user is able to add messages on his name
        and not in the name of other users"""

        """Login as other user2 and post a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id

            c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

        
        """Login as other user1 try to edit the message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            #check unauthorized
            html = resp.get_data(as_text=True) 
            self.assertIn("Access unauthorized.", html)
            #check the message is still int he database
            msg_all = Message.query.all()
            self.assertIn(msg, msg_all)

        



    


    

        
