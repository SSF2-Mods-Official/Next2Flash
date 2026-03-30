package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemTilt_196 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function ItemTilt_196()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame7():*
        {
            this.self.playAttackSound(1);
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-16),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame9():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

