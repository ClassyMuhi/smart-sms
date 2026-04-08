export const conversationsSeed = [
  {
    id: 'alex',
    name: 'Alex Morgan',
    avatar: 'https://i.pravatar.cc/100?img=5',
    status: 'Online now',
    lastMessage: 'Hey bro, are we shipping tonight?',
    time: '2m',
    unread: 2,
    typing: false,
  },
  {
    id: 'design',
    name: 'Design Team',
    avatar: 'https://i.pravatar.cc/100?img=14',
    status: '5 members active',
    lastMessage: 'Meeting tomorrow at 10:00',
    time: '11m',
    unread: 0,
    typing: true,
  },
  {
    id: 'arjun',
    name: 'Arjun',
    avatar: 'https://i.pravatar.cc/100?img=32',
    status: 'Last seen 20m ago',
    lastMessage: 'lol 😂😂😂',
    time: '26m',
    unread: 1,
    typing: false,
  },
  {
    id: 'priya',
    name: 'Priya',
    avatar: 'https://i.pravatar.cc/100?img=45',
    status: 'Online now',
    lastMessage: 'Sent a photo',
    time: '1h',
    unread: 0,
    typing: false,
  },
];

export const messagesSeed = {
  alex: [
    { id: 1, sender: 'them', text: 'Are we still on for tonight?', time: '09:12 AM' },
    { id: 2, sender: 'me', text: 'Yes, frontend is almost polished.', time: '09:14 AM' },
    { id: 3, sender: 'them', text: 'Perfect. Push once done.', time: '09:16 AM', reaction: '🔥' },
  ],
  design: [
    { id: 1, sender: 'them', text: 'Can we adjust spacing on the auth card?', time: 'Yesterday' },
    { id: 2, sender: 'me', text: 'Done. It follows an 8px rhythm now.', time: 'Yesterday' },
  ],
  arjun: [{ id: 1, sender: 'them', text: 'lol 😂😂😂', time: '10:01 AM' }],
  priya: [{ id: 1, sender: 'them', text: 'Sent a photo', time: 'Yesterday' }],
};

export const contactsSeed = [
  { id: 'u1', name: 'Nina Shah', avatar: 'https://i.pravatar.cc/90?img=20' },
  { id: 'u2', name: 'Rahul Menon', avatar: 'https://i.pravatar.cc/90?img=22' },
  { id: 'u3', name: 'Sophia Reed', avatar: 'https://i.pravatar.cc/90?img=28' },
  { id: 'u4', name: 'Ibrahim Ali', avatar: 'https://i.pravatar.cc/90?img=30' },
  { id: 'u5', name: 'Maya Wilson', avatar: 'https://i.pravatar.cc/90?img=36' },
];
