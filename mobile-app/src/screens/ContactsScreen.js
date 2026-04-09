cd "c:\Users\santh\smart sms\smartsms"
& "c:\Users\santh\smart sms\venv\Scripts\Activate.ps1"
python manage.py runserver 0.0.0.0:8000import React, { useEffect, useMemo, useState } from 'react';
import { Alert, FlatList, ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { AppButton, AppTextInput, Card, Screen, SectionTitle } from '../components/Ui';
import { contactApi } from '../services/contactApi';

const getItems = (payload) => {
  if (Array.isArray(payload)) {
    return payload;
  }
  return payload?.results || [];
};

export default function ContactsScreen() {
  const [contacts, setContacts] = useState([]);
  const [emergencyContacts, setEmergencyContacts] = useState([]);
  const [query, setQuery] = useState('');
  const [form, setForm] = useState({ name: '', phone: '', email: '' });
  const [relationship, setRelationship] = useState('');

  const loadContacts = async () => {
    const response = await contactApi.list();
    setContacts(getItems(response));
  };

  const loadEmergency = async () => {
    const response = await contactApi.emergencyList();
    setEmergencyContacts(getItems(response));
  };

  useEffect(() => {
    loadContacts();
    loadEmergency();
  }, []);

  const visibleContacts = useMemo(() => {
    if (!query.trim()) {
      return contacts;
    }
    const q = query.toLowerCase();
    return contacts.filter((item) => item.name?.toLowerCase().includes(q) || item.phone?.toLowerCase().includes(q));
  }, [contacts, query]);

  const addContact = async () => {
    try {
      await contactApi.create(form);
      setForm({ name: '', phone: '', email: '' });
      await loadContacts();
    } catch (error) {
      Alert.alert('Create contact failed', JSON.stringify(error.response?.data || {}));
    }
  };

  const deleteContact = async (id) => {
    try {
      await contactApi.remove(id);
      await loadContacts();
    } catch (error) {
      Alert.alert('Delete failed', JSON.stringify(error.response?.data || {}));
    }
  };

  const markEmergency = async (phone) => {
    try {
      await contactApi.addEmergencyByPhone({ phone, relationship });
      setRelationship('');
      await loadEmergency();
      Alert.alert('Success', 'Added to emergency contacts');
    } catch (error) {
      Alert.alert('Emergency contact failed', JSON.stringify(error.response?.data || {}));
    }
  };

  return (
    <Screen>
      <ScrollView>
        <Card>
          <SectionTitle>Add Contact</SectionTitle>
          <AppTextInput label="Name" placeholder="Contact name" value={form.name} onChangeText={(value) => setForm({ ...form, name: value })} />
          <AppTextInput label="Phone" placeholder="Phone number" value={form.phone} onChangeText={(value) => setForm({ ...form, phone: value })} keyboardType="phone-pad" />
          <AppTextInput label="Email" placeholder="Email address" value={form.email} onChangeText={(value) => setForm({ ...form, email: value })} autoCapitalize="none" keyboardType="email-address" />
          <AppButton title="Save Contact" onPress={addContact} />
        </Card>

        <Card>
          <SectionTitle>Search</SectionTitle>
          <AppTextInput label="Search contacts" placeholder="Type a name or phone" value={query} onChangeText={setQuery} />
        </Card>

        <Card>
          <SectionTitle>Contacts</SectionTitle>
          {visibleContacts.map((item) => (
            <View key={item.id} style={{ paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#1f2937' }}>
              <Text style={{ color: '#fff', fontSize: 16, fontWeight: '700' }}>{item.name}</Text>
              <Text style={{ color: '#cbd5e1' }}>{item.phone}</Text>
              {item.email ? <Text style={{ color: '#94a3b8' }}>{item.email}</Text> : null}
              <View style={{ flexDirection: 'row', gap: 10, marginTop: 10 }}>
                <TouchableOpacity onPress={() => deleteContact(item.id)}>
                  <Text style={{ color: '#f87171' }}>Delete</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => markEmergency(item.phone)}>
                  <Text style={{ color: '#34d399' }}>Emergency</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
          {visibleContacts.length === 0 ? <Text style={{ color: '#94a3b8' }}>No contacts found.</Text> : null}
        </Card>

        <Card>
          <SectionTitle>Emergency Contacts</SectionTitle>
          <AppTextInput label="Relationship label" placeholder="Mother, Doctor, Friend" value={relationship} onChangeText={setRelationship} />
          {emergencyContacts.map((item) => (
            <View key={item.id} style={{ paddingVertical: 10 }}>
              <Text style={{ color: '#fff' }}>{item.contact_detail?.name || item.contact?.name || item.name}</Text>
              <Text style={{ color: '#94a3b8' }}>{item.relationship || 'Emergency Contact'}</Text>
            </View>
          ))}
        </Card>
      </ScrollView>
    </Screen>
  );
}
