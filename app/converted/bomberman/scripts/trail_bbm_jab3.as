package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_jab3 extends MovieClip
    {

        public function trail_bbm_jab3()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

