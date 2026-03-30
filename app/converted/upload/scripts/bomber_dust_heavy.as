package
{
    import flash.display.MovieClip;

    public dynamic class bomber_dust_heavy extends MovieClip
    {

        public function bomber_dust_heavy()
        {
            super();
            addFrameScript(10, this.frame11, 11, this.frame12);
        }

        internal function frame11():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame12():*
        {
            gotoAndPlay("end");
        }


    }
}

