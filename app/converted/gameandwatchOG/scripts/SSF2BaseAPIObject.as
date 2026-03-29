package
{
    public dynamic class SSF2BaseAPIObject
    {

        public var $ext:Object;
        protected var _api:*;

        public function SSF2BaseAPIObject(_arg_1:*):void
        {
            api = _arg_1;
            super();
            _api = api;
            $ext = {"getAPI":function ():*
                {
                    return _api;
                }};
        }

        public function getType():String
        {
            return "SSF2BaseAPIObject";
        }

        public function get metadata():Object
        {
            return (isDisposed()) ? null : _api.metadata;
        }

        public function initialize():void
        {
        }

        public function update():void
        {
        }

        public function isDisposed():Boolean
        {
            return (_api) ? false : true;
        }

        public function dispose():void
        {
        }

        public function __dispose():void
        {
            _api = null;
            $ext = null;
        }

        public function isEqual(_arg_1:*):Boolean
        {
            if (!_arg_1)
            {
            }
            else
            {
            };
            return _arg_1 && (_api === _arg_1.$ext.getAPI());
        }


    }
}

