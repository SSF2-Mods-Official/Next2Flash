package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class dee_nspecprojectile_124 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;

        public function dee_nspecprojectile_124()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10, 28, this.frame29, 29, this.frame30);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame29():*
        {
            this.self.stancePlayFrame("suspend");
        }

        internal function frame30():*
        {
            this.self = SSF2API.getProjectile(this);
            this.self.stancePlayFrame("loop");
        }


    }
}

