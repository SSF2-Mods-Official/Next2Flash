package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemHeavyShoot_205 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function ItemHeavyShoot_205()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-16),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

