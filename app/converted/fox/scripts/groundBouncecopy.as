package
{
    import flash.display.MovieClip;

    public dynamic class groundBouncecopy extends MovieClip
    {

        public function groundBouncecopy()
        {
            super();
            addFrameScript(9, this.frame10);
        }

        internal function frame10():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

