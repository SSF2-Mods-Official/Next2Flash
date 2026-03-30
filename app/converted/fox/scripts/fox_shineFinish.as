package
{
    import flash.display.MovieClip;

    public dynamic class fox_shineFinish extends MovieClip
    {

        public function fox_shineFinish()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

