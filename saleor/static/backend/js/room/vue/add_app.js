$ = jQuery;

var uploadImageUrl = $('.pageUrls').data('uploadimages');
var csrfmiddlewaretoken  = jQuery("[name=csrfmiddlewaretoken]").val();

function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }

var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       'name': 'Add room',
       'autoComplete': true,
       'nightly': null,
       'daytime': null,
       'weekly' : null,
       'daily'  : null,
       'monthly': null
    },
    components: {
        UploadImage
    },
    created:function(){
       console.log('vue running in parent');
       if($('#room_id').val()){
           this.daily = $('#daily').val();
           this.nightly = $('#nightly').val();
           this.daytime = $('#daytime').val();
           this.weekly = $('#weekly').val();
           this.monthly = $('#monthly').val();
       }

       //console.log(today);
    },
    methods:{
        computeFullDay: function(){
          /* check if field auto complete is enabled */
          if(this.autoComplete){
            this.nightly = this.daily / 2;
            this.daytime = this.daily / 2;
            this.weekly = (parseInt(this.daytime) + parseInt(this.nightly)) * 7;
            this.monthly = (parseInt(this.daytime) + parseInt(this.nightly)) * 30;
          }
        },
        computeHalfDay:function(){
            /* check if field auto complete is enabled */
            if(this.autoComplete){
                this.monthly = (parseInt(this.daytime) + parseInt(this.nightly)) * 30
                this.weekly  = (parseInt(this.daytime) + parseInt(this.nightly)) * 7
            }
        }
    }
});

var UploadImage = Vue.component('upload-image', {
        template: '#uploader-temp',
        props: {
            url: {
                type: String,
                required: true,
                default: null
            },
            name: {
                type: String,
                required: false,
                default: 'images[]'
            },
            max_batch: {
                type: Number,
                required: false,
                default: 0
            },
            max_files: {
                type: Number,
                required: false,
                default: 10
            },
            max_filesize: {
                type: Number,
                required: false,
                default: 8000
            },
            button_html: {
                type: String,
                required: false,
                default: 'Upload Images'
            },
            button_class: {
                type: String,
                required: false,
                default: 'btn btn-primary'
            },
        },
        data: function(){
            return {
                form: null,
                input: null,
                index: 0,
                total: 0,
                files: {},
                image: {},
                batch: {},
                onDragover: false,
                onUploading: false
            }
        },
        mounted: function(){
            this.form = document.getElementById('upload_image_form--' + this.name);
            this.input = document.getElementById('upload_image_form__input--' + this.name);

            ['drag', 'dragstart', 'dragend',
                'dragover', 'dragenter', 'dragleave', 'drop'].forEach(event => this.form.addEventListener(event, (e) => {
                e.preventDefault(); e.stopPropagation();
            }));

            ['dragover', 'dragenter']
                .forEach(event => this.form.addEventListener(event, this.dragEnter));

            ['dragleave', 'dragend', 'drop']
                .forEach(event => this.form.addEventListener(event, this.dragLeave));

            ['drop']
                .forEach(event => this.form.addEventListener(event, this.fileDrop));

            ['change']
                .forEach(event => this.input.addEventListener(event, this.fileDrop));

            this.form.addEventListener('click', (e) => {
                this.input.click();
            });
        },
        methods: {
            _can_xhr(){
                if(this.total >= this.max_files){
                    return false;
                }
                return true;
            },
            _can_upload_file(key){
                let file = this.files[key];

                if(file.attempted || file.bad_size){
                    return false;
                }
                return true;
            },
            _xhr: function(formData, keys, callback){
                this.onUploading = true;
                this.$emit('upload-image-attempt', formData);

                keys.forEach((key) => {
                    Vue.set(this.files[key], 'attempted', true);
                });

                this.$http.post(this.url, formData).then((response) => {
                    keys.forEach((key) => {
                        Vue.set(this.files[key], 'uploaded', true);
                        this.total++;
                    });

                    alertUser('Image added successfully');
                    this.$emit('upload-image-success', [formData, response]);
                }, (response) => {
                    this.$emit('upload-image-failure', [formData, response]);
                }).then((response) => {
                    this.onUploading = false;

                    callback();
                });
            },
            upload: function(){
                if(!this._can_xhr()) return false;

                for (let key in this.files) {
                    if(!this._can_upload_file(key)) continue;

                    let formData = new FormData();
                    formData.append(this.name, this.files[key]);
                    formData.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

                    this._xhr(formData, [key], this.upload);

                    return true;
                }
            },
            upload_batch: function(){
                if(!this._can_xhr()) return false;

                for (let key in this.batch) {
                    this._xhr(this.batch[key].form, this.batch[key].keys, this.upload_batch);

                    delete this.batch[key];

                    return true;
                }
            },
            create_batch: function(){
                let index = 0;
                let count = 0;

                this.batch = {};

                for (let key in this.files) {
                    if(!this._can_upload_file(key)) continue;

                    if(this.batch[index] == null || count == this.max_batch){
                        index++;
                        count = 0;
                        this.batch[index] = {form:new FormData(), keys:[]};
                    }

                    count++;
                    this.batch[index]['keys'].push(key);
                    this.batch[index]['form'].append(this.name, this.files[key]);
                }
            },
            submit: function(e){
                e.preventDefault(); e.stopPropagation();

                if(!this.onUploading){
                    if(this.max_batch > 1){
                               this.create_batch();
                        return this.upload_batch();
                    }
                    this.upload();
                }
            },
            dragEnter: function(e){
                e.preventDefault();
                this.onDragover = true;
            },
            dragLeave: function(e){
                e.preventDefault();
                this.onDragover = false;
            },
            fileDrop: function(e){
                e.preventDefault();

                let newFiles = e.target.files || e.dataTransfer.files;

                for(let i = 0; i < newFiles.length; i++){
                    Vue.set(this.files, this.index, newFiles[i]);
                    this.fileInit(this.index);
                    this.fileRead(this.index);

                    this.index++;
                }

                e.target.value = '';
            },
            fileInit: function(key){
                let file = this.files[key];

                if((file.size * 0.001) > this.max_filesize){
                    Vue.set(this.files[key], 'bad_size', true);
                }
            },
            fileRead: function(key){
                let reader = new FileReader();

                reader.addEventListener("load", (e) => {
                    Vue.set(this.image, key, reader.result);
                });

                reader.readAsDataURL(this.files[key]);
            },
            fileDelete: function(e, key){
                Vue.delete(this.files, key);
                Vue.delete(this.image, key);
            },
            fileView: function(e, key){
                e.preventDefault(); e.stopPropagation();
            }
        }
    });


new Vue({
    el:"#vue-app2",
    template: '<upload-image url="'+uploadImageUrl+'"></upload-image>',
    components: {
        UploadImage
    }
})