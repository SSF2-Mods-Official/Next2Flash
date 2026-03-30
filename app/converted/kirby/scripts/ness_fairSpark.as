package
{
    import flash.display.MovieClip;

    public dynamic class ness_fairSpark extends MovieClip
    {

        public function ness_fairSpark()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

