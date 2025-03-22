const express = require('express');
const router = express.Router();
const { getContacts, addContact } = require('../controllers/contactsController');

// Get all contacts
router.get('/', getContacts);

// Add a new contact
router.post('/', addContact);

module.exports = router;
