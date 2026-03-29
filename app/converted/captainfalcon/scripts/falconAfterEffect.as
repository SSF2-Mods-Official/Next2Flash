package
{
    import flash.display.MovieClip;

    public dynamic class falconAfterEffect extends MovieClip
    {

        public function falconAfterEffect()
        {
            super();
            addFrameScript(15, this.frame16);
        }

        internal function frame16():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

