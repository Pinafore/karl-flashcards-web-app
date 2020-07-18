<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>
        Manage Users
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn to="/main/admin/users/create">Create User</v-btn>
    </v-toolbar>
    <v-data-table :headers="headers" :items="users">
      <template v-slot:item.is_active="{ item }">
        <v-icon v-if="item.is_active">mdi-check</v-icon>
      </template>

      <template v-slot:item.is_superuser="{ item }">
        <v-icon v-if="item.is_superuser">mdi-check</v-icon>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-icon @click="routeEditUser(item.id)">mdi-pencil</v-icon>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { adminStore } from "@/store";

  @Component
  export default class AdminUsers extends Vue {
    public headers = [
      {
        text: "Email",
        sortable: true,
        value: "email",
        align: "left",
      },
      {
        text: "Username",
        sortable: true,
        value: "username",
        align: "left",
      },
      {
        text: "Repetition Model",
        sortable: true,
        value: "repetition_model",
        align: "left",
      },
      {
        text: "Is Active",
        sortable: true,
        value: "is_active",
        align: "left",
      },
      {
        text: "Is Superuser",
        sortable: true,
        value: "is_superuser",
        align: "left",
      },
      {
        text: "Actions",
        value: "actions",
      },
    ];

    get users() {
      return adminStore.users;
    }

    async mounted() {
      await adminStore.getUsers();
    }

    routeEditUser(id: string) {
      this.$router.push({ name: "main-admin-users-edit", params: { id } });
    }
  }
</script>
