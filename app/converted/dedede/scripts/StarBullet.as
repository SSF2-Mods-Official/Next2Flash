package
{
    import flash.geom.Point;

    public dynamic class StarBullet extends SSF2Projectile
    {

        public var EXHALE_DURATION:int = 14;
        public var SPIT_DAMAGE:int = 14;
        private var _foe:SSF2Character;
        private var _point:Point;

        public function StarBullet(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getOwnStats():Object
        {
            return {
                "classAPI":StarBullet,
                "linkage_id":"dedede_starbullet",
                "inheritPalette":true,
                "yoffset":-40,
                "width":27,
                "height":33,
                "time_max":(this.EXHALE_DURATION + 1),
                "xspeed":14,
                "xdecay":0
            };
        }

        override public function getAttackStats():Object
        {
            return {"attack_idle":{
                    "refreshRate":-1,
                    "attackBoxes":{"attackBox":{
                            "damage":12,
                            "reversableAngle":false,
                            "selfHitStun":0,
                            "effect_id":"effect_swordSlash",
                            "direction":90,
                            "power":85,
                            "kbConstant":95,
                            "effectSound":"sw_brawl_hit_M"
                        }}
                }};
        }

        override public function initialize():void
        {
            addEventListener(SSF2Event.ATTACK_HIT, this.onAttackHit, {"persistent":true});
            addEventListener(SSF2Event.HIT_WALL, this.onWallHit, {"persistent":true});
            addEventListener(SSF2Event.PROJ_DESTROYED, this.onDestroyed, {"persistent":true});
            this._point = new Point();
        }

        override public function update():void
        {
            this._point.x = getX();
            this._point.y = getY();
            this.onWallHit(null);
            return;
            this.syncFoe();
        }

        private function onAttackHit(_arg_1:*):*
        {
        }

        private function onWallHit(_arg_1:*):*
        {
            this.releaseFoe(true);
            destroy();
        }

        private function onDestroyed(_arg_1:*):*
        {
            if (this._foe)
            {
                this.releaseFoe(this._foe.inState(CState.CAUGHT));
            };
        }

        private function onFoeStateChanged(_arg_1:*):*
        {
            if (!this._foe)
            {
                return;
            };
            this.releaseFoe();
            destroy();
        }

        private function releaseFoe(_arg_1:Boolean=false):*
        {
            if (!this._foe)
            {
                return;
            };
            this._foe.removeEventListener(SSF2Event.STATE_CHANGE, this.onFoeStateChanged);
            this._foe.release();
            this._foe.setX(getX());
            this._foe.setY(getY());
            this._foe.resetMovement();
            this._foe.resetKnockback();
            if (_arg_1)
            {
                this._foe.unnattachFromGround();
                this._foe.setYSpeed(-12);
            };
            this._foe.setVisibility(true);
            this._foe = null;
        }

        public function syncFoe():void
        {
            if (!this._foe)
            {
                return;
            };
            this._foe.setX(getX());
            this._foe.setY(getY());
        }

        public function grabFoe(_arg_1:SSF2Character):*
        {
            var _local_2:* = _arg_1.grab(-1, false, true, true);
            if (_local_2)
            {
                this._foe = _arg_1;
                this._foe.setVisibility(false);
                this._foe.takeDamage({
                    "damage":this.SPIT_DAMAGE,
                    "hasEffect":false,
                    "atk_id":getAttackStat("atk_id")
                }, this);
                this._foe.addEventListener(SSF2Event.STATE_CHANGE, this.onFoeStateChanged, {"persistent":true});
                this.syncFoe();
            };
        }


    }
}

