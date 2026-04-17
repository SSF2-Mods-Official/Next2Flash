package
{
    import flash.display.MovieClip;

    public dynamic class fox_illusionblur extends MovieClip
    {

        public function fox_illusionblur()
        {
            super();
            addFrameScript(2, this.frame3);
        }

        internal function frame3():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

