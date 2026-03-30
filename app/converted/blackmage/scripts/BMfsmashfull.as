package
{
    import flash.display.MovieClip;

    public dynamic class BMfsmashfull extends MovieClip
    {

        public var stance:MovieClip;

        public function BMfsmashfull()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            stop();
        }


    }
}

