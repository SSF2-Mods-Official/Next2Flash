// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemScrew_96

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemScrew_96 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hand:MovieClip;
        internal var hitBox:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var speed:*;
        internal var updateStats:*;

        public function ItemScrew_96()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 6, this.frame7, 8, this.frame9, 10, this.frame11, 11, this.frame12, 14, this.frame15, 18, this.frame19, 50, this.frame51);
        }

        public function moveUp(_arg_1:*=null):*
        {
            this.self.setYSpeed(this.speed);
            if (this.updateStats)
            {
                this.self.updateAttackBoxStats(1, {"power":(-(this.speed) * 5)});
                this.self.updateAttackBoxStats(2, {"power":(-(this.speed) * 4)});
            };
            this.speed = (this.speed + 2);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:BlackMageExt;
            var _local_7:*;
            var _local_8:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.speed = -23;
            this.updateStats = true;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            };
        }

        internal function frame2():*
        {
            this.self.setXSpeed((this.self.getXSpeed() / 2));
            this.self.playSound("screw1");
        }

        internal function frame3():*
        {
            this.self.createTimer(1, 10, this.moveUp);
            this.self.setYSpeed(-23);
            this.self.playSound("screw2");
        }

        internal function frame7():*
        {
            this.self.playSound("screw3");
        }

        internal function frame9():*
        {
            this.updateStats = false;
            this.self.updateAttackBoxStats(1, {
                "power":30,
                "kbConstant":100,
                "damage":2,
                "hitStun":2,
                "selfHitStun":1
            });
            this.self.updateAttackBoxStats(2, {
                "power":0,
                "kbConstant":100,
                "damage":2,
                "hitStun":2,
                "selfHitStun":1
            });
            this.self.updateAttackStats({"refreshRate":1});
        }

        internal function frame11():*
        {
            this.self.playSound("screw4");
            this.self.setIASA(true);
        }

        internal function frame12():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":80,
                "kbConstant":100,
                "damage":2,
                "hitStun":5,
                "selfHitStun":5
            });
            this.self.updateAttackBoxStats(2, {
                "power":80,
                "kbConstant":100,
                "damage":2,
                "hitStun":5,
                "selfHitStun":5
            });
            this.self.updateAttackStats({"refreshRate":90});
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.playSound("screw5");
            this.self.updateAttackStats({"air_ease":(4 + (this.self.getCharacterStat("max_ySpeed") * 0.4))});
        }

        internal function frame19():*
        {
            this.self.playSound("screw6");
        }

        internal function frame51():*
        {
            gotoAndStop("fallLoop");
        }


    }
}//package blackmage_fla

