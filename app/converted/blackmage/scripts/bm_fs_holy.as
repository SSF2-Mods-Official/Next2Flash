package
{
    import flash.display.MovieClip;

    public dynamic class bm_fs_holy extends MovieClip
    {

        public var stance:MovieClip;

        public function bm_fs_holy()
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

