package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class samus_chargeshot_293 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var speed:Number;
        public var time:int;
        public var character:*;
        public var dmg:Number;
        public var bkb:Number;
        public var kbg:Number;
        public var charge:int;
        public var max:int;
        public var scale:Number;

        public function samus_chargeshot_293()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12);
        }

        public function destroy(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.destroy);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.destroy);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.destroy);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.destroy);
            this.self.destroy();
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.speed = 0;
            this.time = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.dmg = this.self.getAttackBoxStat(1, "damage");
                this.bkb = this.self.getAttackBoxStat(1, "power");
                this.kbg = this.self.getAttackBoxStat(1, "kbConstant");
                this.charge = this.character.getGlobalVariable("SamusNSpecCharge");
                this.max = this.character.getAttackStat("chargetime_max");
                this.scale = 1;
                this.character.setGlobalVariable("SamusNSpecCharge", 0);
                if (this.charge < this.max)
                {
                    this.scale = (0.2 + ((this.charge / this.max) * 0.8));
                    this.dmg += (18 * (this.charge / (this.max - 1)));
                    this.bkb += (22 * (this.charge / (this.max - 1)));
                    this.kbg += (24 * (this.charge / (this.max - 1)));
                    this.self.updateAttackBoxStats(1, {
                        "damage":this.dmg,
                        "power":this.bkb,
                        "kbConstant":this.kbg
                    });
                };
                this.self.setScale(this.scale, this.scale);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.destroy);
            };
        }

        internal function frame12():*
        {
            gotoAndStop("loop");
        }


    }
}

