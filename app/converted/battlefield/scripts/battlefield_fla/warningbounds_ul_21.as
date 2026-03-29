package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class warningbounds_ul_21 extends MovieClip
    {

        public var type:String;

        public function warningbounds_ul_21()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "l_bound_upper";
            this.visible = false;
        }


    }
}

