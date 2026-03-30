package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DThrow_64 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;

        public function DThrow_64()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 12, this.frame13, 14, this.frame15, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.xframe = null;
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame13():*
        {
            this.self.refreshAttackID();
            this.self.playSound("throw_woosh");
        }

        internal function frame15():*
        {
            this.self.playAttackSound(2);
            SSF2API.getCamera().shake(10);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

