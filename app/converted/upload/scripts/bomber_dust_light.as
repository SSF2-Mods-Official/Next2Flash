package
{
    import flash.display.MovieClip;

    public dynamic class bomber_dust_light extends MovieClip
    {

        public function bomber_dust_light()
        {
            super();
            addFrameScript(5, this.frame6, 6, this.frame7);
        }

        internal function frame6():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame7():*
        {
            gotoAndPlay("end");
        }


    }
}

