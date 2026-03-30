package
{
    import flash.display.MovieClip;

    public dynamic class bomber_dust_cloud extends MovieClip
    {

        public function bomber_dust_cloud()
        {
            super();
            addFrameScript(27, this.frame28, 28, this.frame29);
        }

        internal function frame28():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame29():*
        {
            gotoAndPlay("end");
        }


    }
}

