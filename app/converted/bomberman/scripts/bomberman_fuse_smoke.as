package
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fuse_smoke extends MovieClip
    {

        public function bomberman_fuse_smoke()
        {
            super();
            addFrameScript(13, this.frame14, 14, this.frame15);
        }

        internal function frame14():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame15():*
        {
            this.gotoAndStop("end");
        }


    }
}

