from model_bakery import baker

from conversate.models import Message, Room


def test_message_render__emoji_markdown(admin_user):
    room = baker.make(Room, users=[admin_user])
    msg = Message.objects.create(room=room, user=admin_user, content=":thumbsup: *em*")
    assert msg.render() == "<p>\U0001F44D <em>em</em></p>\n"
