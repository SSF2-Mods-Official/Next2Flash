package
{
   public dynamic class SSF2BaseAPIObject
   {
      public var $ext:Object;
      
      protected var _api:*;
      
      public function SSF2BaseAPIObject(param1:*)
      {
         var _arg_1:* = param1;
         api = _arg_1;
         super();
         this._api = api;
         this.$ext = {"getAPI":function():*
         {
            return _api;
         }};
      }
      
      public function getType() : String
      {
         return "SSF2BaseAPIObject";
      }
      
      public function get metadata() : Object
      {
         return this.isDisposed() ? null : this._api.metadata;
      }
      
      public function initialize() : void
      {
      }
      
      public function update() : void
      {
      }
      
      public function isDisposed() : Boolean
      {
         return this._api ? false : true;
      }
      
      public function dispose() : void
      {
      }
      
      public function __dispose() : void
      {
         this._api = null;
         this.$ext = null;
      }
      
      public function isEqual(param1:*) : Boolean
      {
         if(param1)
         {
         }
         return param1 && this._api === param1.$ext.getAPI();
      }
   }
}

