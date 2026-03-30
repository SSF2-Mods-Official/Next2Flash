package
{
    import flash.display.MovieClip;

    public dynamic class groundBounceFront extends MovieClip
    {

        public function groundBounceFront()
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

