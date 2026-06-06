<template>
  <div class="dropdown">
    <button @click.stop="toggle" class="dropbtn">{{ selectedOption || "Select an option" }}</button>
    <div v-if="active" class="dropdown-content">
      <a v-for="option in options" :key="option" @click.stop="selectOption(option)">{{ option }}</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DropDownMenu',
  props: {
    options: {
      type: Array,
      required: true
    },
    darkMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      active: false,
      selectedOption: null
    };
  },
  methods: {
    toggle() {
      this.active = !this.active;
    },
    selectOption(option) {
      this.selectedOption = option;
      this.active = false; 
      this.$emit('select', option);
    }
  }
};
</script>

<style scoped>
.dropdown {
  min-width: 160px;
  position: relative;
}

.dropbtn {
  background-color: #333333;
  color: white;
  padding: 5px 10px;
  font-size: 16px;
  border: 1px solid #464646;
  border-radius: 4px;
  text-align: left;
  cursor: pointer;
  width: 100%;
}

.dropdown-content {
  position: absolute;
  background-color: #333333;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
  border-radius: 0 0 8px 8px;
}

.dropdown-content a {
  color: rgb(255, 255, 255);
  padding: 5px 16px;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: #797979;
}
</style>
