package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class BatSwingRing_102 extends MovieClip
    {

        public var self:*;
        public var owner:*;

        public function BatSwingRing_102()
        {
            super();
            addFrameScript(0, this.frame1, 18, this.frame19, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (this.self && SSF2API.isReady())
            {
                this.owner = this.self.getOwner();
            };
        }

        internal function frame19():*
        {
            if ((this.owner.getCurrentAttackFrame() == "b_up") || (this.owner.getCurrentAttackFrame() == "b_up_air"))
            {
                gotoAndStop("loop");
            }
            else
            {
                gotoAndStop("destroy");
            };
        }

        internal function frame22():*
        {
            this.self.destroy();
        }


    }
}

