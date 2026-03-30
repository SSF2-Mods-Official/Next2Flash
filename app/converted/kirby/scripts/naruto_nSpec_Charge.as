package
{
    import flash.display.MovieClip;

    public dynamic class naruto_nSpec_Charge extends MovieClip
    {

        public function naruto_nSpec_Charge()
        {
            super();
            addFrameScript(14, this.frame15);
        }

        internal function frame15():*
        {
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

